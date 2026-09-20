"""Qvant ledgeri, questlar, streak, do'kon va Activity reyting.

DoD: Qvant ledgerida qamrov MAJBURIY.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import User
from judging.models import Attempt
from judging.services import apply_result
from profiles.models import UserAchievement
from qvant import ledger, quests, streak
from qvant.models import (
    DAILY_EARN_CAP,
    QvantTransaction,
    QvantWallet,
    ShopItem,
    UserInventory,
    UserQuestCompletion,
)
from qvant.services import PurchaseError, purchase, recalc_activity
from ratings.models import RatingHistory


@pytest.fixture
def catalogue(db) -> None:
    quests.sync_catalogue()
    ShopItem.objects.create(
        code="streak-freeze",
        category=ShopItem.Category.STREAK_FREEZE,
        title_uz="Freeze",
        price=200,
        is_consumable=True,
    )
    ShopItem.objects.create(
        code="frame-bronze",
        category=ShopItem.Category.AVATAR_FRAME,
        title_uz="Ramka",
        price=500,
    )


@pytest.mark.django_db
class TestLedger:
    def test_credit_balansni_oshiradi(self, user) -> None:
        tx = ledger.credit(user, 50, QvantTransaction.Reason.QUEST)
        assert tx is not None
        assert tx.balance_after == 50
        assert ledger.get_wallet(user).balance == 50

    def test_debit_balansni_kamaytiradi(self, user) -> None:
        ledger.credit(user, 100, QvantTransaction.Reason.ADMIN)
        tx = ledger.debit(user, 30, QvantTransaction.Reason.PURCHASE)
        assert tx.amount == -30
        assert ledger.get_wallet(user).balance == 70

    def test_yetarsiz_balans(self, user) -> None:
        with pytest.raises(ledger.InsufficientBalance):
            ledger.debit(user, 10, QvantTransaction.Reason.PURCHASE)
        assert ledger.get_wallet(user).balance == 0

    def test_balans_ledgerdan_chiqadi(self, user) -> None:
        """Kesh va ledger yig'indisi HAR DOIM mos kelishi kerak."""
        ledger.credit(user, 100, QvantTransaction.Reason.ADMIN)
        ledger.credit(user, 50, QvantTransaction.Reason.QUEST)
        ledger.debit(user, 30, QvantTransaction.Reason.PURCHASE)
        cached, from_ledger = ledger.verify_balance(user)
        assert cached == from_ledger == 120

    def test_kunlik_shift(self, user) -> None:
        """ADR-0002 anti-farm: kuniga maksimal 100 Qvant."""
        ledger.credit(user, 80, QvantTransaction.Reason.QUEST)
        tx = ledger.credit(user, 50, QvantTransaction.Reason.QUEST)
        assert tx is not None
        assert tx.amount == 20  # qisman berildi
        assert ledger.get_wallet(user).balance == DAILY_EARN_CAP

    def test_shift_toldirilgach_bermaydi(self, user) -> None:
        ledger.credit(user, DAILY_EARN_CAP, QvantTransaction.Reason.QUEST)
        assert ledger.credit(user, 10, QvantTransaction.Reason.QUEST) is None

    def test_streak_shiftdan_ozod(self, user) -> None:
        """ADR-0002: «streak yutuqlari bundan tashqari»."""
        ledger.credit(user, DAILY_EARN_CAP, QvantTransaction.Reason.QUEST)
        tx = ledger.credit(user, 250, QvantTransaction.Reason.STREAK)
        assert tx is not None and tx.amount == 250

    def test_qaytarish(self, user) -> None:
        ledger.credit(user, 60, QvantTransaction.Reason.QUEST, ref_type="attempt", ref_id="7")
        assert ledger.refund_ref(user, "attempt", "7") == 60
        assert ledger.get_wallet(user).balance == 0

    def test_qaytarish_manfiyga_tushirmaydi(self, user) -> None:
        """Foydalanuvchi sarflab bo'lgan bo'lsa — mavjud balansgacha."""
        ledger.credit(user, 60, QvantTransaction.Reason.QUEST, ref_type="attempt", ref_id="7")
        ledger.debit(user, 50, QvantTransaction.Reason.PURCHASE)
        assert ledger.refund_ref(user, "attempt", "7") == 10
        assert ledger.get_wallet(user).balance == 0

    def test_ikki_marta_qaytarilmaydi(self, user) -> None:
        ledger.credit(user, 60, QvantTransaction.Reason.QUEST, ref_type="attempt", ref_id="7")
        ledger.refund_ref(user, "attempt", "7")
        assert ledger.refund_ref(user, "attempt", "7") == 0

    def test_manfiy_credit_rad_etiladi(self, user) -> None:
        with pytest.raises(ValueError):
            ledger.credit(user, -5, QvantTransaction.Reason.ADMIN)


@pytest.mark.django_db
class TestQuests:
    def test_kunlik_quest_bir_marta(self, user, catalogue) -> None:
        key = quests.day_key()
        assert quests.award(user, quests.DAILY_SOLVE, key) == 10
        assert quests.award(user, quests.DAILY_SOLVE, key) == 0
        assert UserQuestCompletion.objects.count() == 1

    def test_boshqa_kun_yangi_mukofot(self, user, catalogue) -> None:
        today = timezone.localdate()
        assert quests.award(user, quests.DAILY_SOLVE, quests.day_key(today)) == 10
        assert (
            quests.award(user, quests.DAILY_SOLVE, quests.day_key(today - timedelta(days=1))) == 10
        )

    def test_uch_ac_questi(self, user, catalogue) -> None:
        granted = quests.on_accepted(user, ac_count_today=3)
        assert quests.DAILY_THREE_AC in granted

    def test_ikki_ac_uchinchi_questni_bermaydi(self, user, catalogue) -> None:
        granted = quests.on_accepted(user, ac_count_today=2)
        assert quests.DAILY_THREE_AC not in granted

    def test_streak_yutuqlari(self, user, catalogue) -> None:
        assert quests.STREAK_7 in quests.on_streak_reached(user, 7)
        assert quests.on_streak_reached(user, 8) == []
        assert quests.STREAK_7 in quests.on_streak_reached(user, 14)
        granted30 = quests.on_streak_reached(user, 30)
        assert quests.STREAK_30 in granted30

    def test_profil_umrbod_bir_marta(self, user, catalogue) -> None:
        assert quests.on_profile_completed(user) == 50
        assert quests.on_profile_completed(user) == 0

    def test_shift_questni_bekor_qilmaydi(self, user, catalogue) -> None:
        """Shift Qvant ni kamaytiradi, lekin quest BAJARILGAN bo'lib qoladi.

        Activity reyting quest SONINI sanaydi, Qvant miqdorini emas.
        """
        ledger.credit(user, DAILY_EARN_CAP, QvantTransaction.Reason.QUEST)
        assert quests.award(user, quests.DAILY_SOLVE, quests.day_key()) == 0
        assert UserQuestCompletion.objects.filter(quest__code=quests.DAILY_SOLVE).exists()


@pytest.mark.django_db
class TestStreak:
    def test_birinchi_kun(self, user, catalogue) -> None:
        count, _ = streak.touch(user)
        assert count == 1

    def test_ketma_ket_kunlar(self, user, catalogue) -> None:
        today = timezone.localdate()
        streak.touch(user, today - timedelta(days=2))
        streak.touch(user, today - timedelta(days=1))
        count, _ = streak.touch(user, today)
        assert count == 3

    def test_bir_kunda_bir_marta(self, user, catalogue) -> None:
        streak.touch(user)
        count, granted = streak.touch(user)
        assert count == 1 and granted == []

    def test_tashlangan_kun_uzadi(self, user, catalogue) -> None:
        today = timezone.localdate()
        streak.touch(user, today - timedelta(days=5))
        count, _ = streak.touch(user, today)
        assert count == 1

    def test_freeze_boshliqni_yopadi(self, user, catalogue) -> None:
        today = timezone.localdate()
        streak.touch(user, today - timedelta(days=2))
        user.refresh_from_db()
        streak.apply_freeze(user, days=3)
        user.refresh_from_db()
        count, _ = streak.touch(user, today)
        assert count == 2  # uzilmadi

    def test_dokondan_olingan_bir_kunlik_freeze_ishlaydi(self, user, catalogue) -> None:
        """Do'kon `days=1` beradi — mavjud test esa `days=3` bilan sinardi.

        O'lchandi: bir kunlik muzlatgich bilan streak 5 dan 1 ga tushardi,
        chunki taqqoslash tashlangan kun o'rniga qaytilgan kun bilan
        qilinardi.
        """
        today = timezone.localdate()
        item = ShopItem.objects.create(
            code="freeze-1",
            category=ShopItem.Category.STREAK_FREEZE,
            title_uz="Muzlatgich",
            price=50,
            is_consumable=True,
        )
        ledger.credit(user, 100, QvantTransaction.Reason.ADMIN)

        streak.touch(user, today - timedelta(days=2))
        purchase(user, item.code)  # kecha emas, ikki kun oldin faol edi
        user.refresh_from_db()
        assert user.streak_freeze_until == today + timedelta(days=1)

        count, _ = streak.touch(user, today)

        assert count == 2  # kechagi bo'shliq kechirildi
        user.refresh_from_db()
        assert user.streak_freeze_until is None  # sarflandi

    def test_freeze_ikki_kunlik_boshliqni_yopmaydi(self, user, catalogue) -> None:
        """Bir kunlik muzlatgich faqat BIR kunni kechiradi.

        `apply_freeze` doim haqiqiy bugundan hisoblaydi, shuning uchun
        uch kun oldin sotib olingan muzlatgich qo'lda qo'yiladi: o'shanda
        `days=1` aynan shu qiymatni bergan bo'lardi.
        """
        today = timezone.localdate()
        streak.touch(user, today - timedelta(days=3))
        User.objects.filter(pk=user.pk).update(streak_freeze_until=today - timedelta(days=2))
        user.refresh_from_db()

        # Ikki kun tashlandi (kecha va undan oldin), muzlatgich bittasini
        # yopadi — zanjir baribir uziladi.
        count, _ = streak.touch(user, today)

        assert count == 1

    def test_yetti_kunda_yutuq(self, user, catalogue) -> None:
        today = timezone.localdate()
        for i in range(7, 0, -1):
            _, granted = streak.touch(user, today - timedelta(days=i - 1))
        assert quests.STREAK_7 in granted


@pytest.mark.django_db
class TestActivityRating:
    def test_formula_qollaniladi(self, user, catalogue, problem, language) -> None:
        Attempt.objects.create(user=user, problem=problem, language=language, source_code="x")
        quests.award(user, quests.DAILY_SOLVE, quests.day_key())
        user.streak_count = 5
        user.save()
        value = recalc_activity(user)
        # 10×1 faol kun + 5×1 quest + min(2×5, 60) = 25
        assert value == 25

    def test_ozgarish_yoziladi(self, user, catalogue, problem, language) -> None:
        Attempt.objects.create(user=user, problem=problem, language=language, source_code="x")
        recalc_activity(user)
        entry = RatingHistory.objects.filter(user=user, rating_type="activity").first()
        assert entry is not None and entry.delta > 0

    def test_balans_activity_ga_tasir_qilmaydi(self, user, catalogue) -> None:
        """ADR-0002: Qvant BALANSI formulada yo'q.

        Aks holda do'konda xarid reytingni tushirardi.
        """
        ledger.credit(user, 900, QvantTransaction.Reason.ADMIN)
        before = recalc_activity(user)
        ledger.debit(user, 500, QvantTransaction.Reason.PURCHASE)
        assert recalc_activity(user) == before


@pytest.mark.django_db
class TestShop:
    def test_xarid(self, user, catalogue) -> None:
        ledger.credit(user, 600, QvantTransaction.Reason.ADMIN)
        entry = purchase(user, "frame-bronze")
        assert entry.item.code == "frame-bronze"
        assert ledger.get_wallet(user).balance == 100

    def test_balans_yetmasa(self, user, catalogue) -> None:
        with pytest.raises(PurchaseError):
            purchase(user, "frame-bronze")
        assert not UserInventory.objects.exists()

    def test_takrorlanmaydigan_narsa(self, user, catalogue) -> None:
        ledger.credit(user, 1200, QvantTransaction.Reason.ADMIN)
        purchase(user, "frame-bronze")
        with pytest.raises(PurchaseError):
            purchase(user, "frame-bronze")

    def test_sarflanadigan_narsa_takrorlanadi(self, user, catalogue) -> None:
        ledger.credit(user, 500, QvantTransaction.Reason.ADMIN)
        purchase(user, "streak-freeze")
        purchase(user, "streak-freeze")
        assert UserInventory.objects.filter(user=user).count() == 2

    def test_streak_freeze_darhol_yoqiladi(self, user, catalogue) -> None:
        ledger.credit(user, 300, QvantTransaction.Reason.ADMIN)
        purchase(user, "streak-freeze")
        user.refresh_from_db()
        assert user.streak_freeze_until is not None


@pytest.mark.django_db
class TestJudgeIntegration:
    def test_ac_qvant_va_streak_beradi(self, user, catalogue, problem, language) -> None:
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        user.refresh_from_db()
        assert ledger.get_wallet(user).balance > 0
        assert user.streak_count == 1
        assert user.rating_activity > 0

    def test_qayta_yechish_qvant_bermaydi(self, user, catalogue, problem, language) -> None:
        """ADR-0002: faqat birinchi AC ball beradi."""
        for _ in range(2):
            attempt = Attempt.objects.create(
                user=user, problem=problem, language=language, source_code="x"
            )
            apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        # Bitta daily_solve va «birinchi masala» yutug'i — ikkinchi AC hech narsa bermaydi.
        assert QvantWallet.objects.get(user=user).balance == 20

    def test_rejudge_ac_ni_bekor_qilsa(self, user, catalogue, problem, language) -> None:
        """AC bekor qilinsa Skills tushadi va yechilgan yozuv olib tashlanadi."""
        from ratings.models import UserSolvedProblem

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        user.refresh_from_db()
        assert user.rating_skills == 800

        apply_result({"attempt_id": attempt.pk, "verdict": "WA"})
        user.refresh_from_db()
        assert user.rating_skills == 0
        assert not UserSolvedProblem.objects.filter(user=user).exists()


@pytest.mark.django_db
class TestApi:
    def _client(self, user) -> APIClient:
        c = APIClient()
        c.force_authenticate(user=user)
        return c

    def test_wallet(self, user, catalogue) -> None:
        ledger.credit(user, 40, QvantTransaction.Reason.QUEST)
        body = self._client(user).get(reverse("qvant-wallet")).json()
        assert body["balance"] == 40
        assert body["earned_today"] == 40
        assert body["remaining_today"] == DAILY_EARN_CAP - 40

    def test_ledger_royxati(self, user, catalogue) -> None:
        ledger.credit(user, 10, QvantTransaction.Reason.QUEST)
        body = self._client(user).get(reverse("qvant-tx-list")).json()
        assert body["results"][0]["amount"] == 10

    def test_questlar(self, user, catalogue) -> None:
        quests.award(user, quests.DAILY_SOLVE, quests.day_key())
        body = self._client(user).get(reverse("qvant-quests")).json()
        done = {q["code"]: q["done"] for q in body}
        assert done[quests.DAILY_SOLVE] is True
        assert done[quests.DAILY_THREE_AC] is False

    def test_dokon_xaridi(self, user, catalogue) -> None:
        ledger.credit(user, 600, QvantTransaction.Reason.ADMIN)
        r = self._client(user).post(reverse("qvant-shop-purchase"), {"item": "frame-bronze"})
        assert r.status_code == 201
        assert (
            self._client(user).get(reverse("qvant-inventory-list")).json()[0]["item"]["code"]
            == "frame-bronze"
        )

    def test_balans_yetmasa_400(self, user, catalogue) -> None:
        r = self._client(user).post(reverse("qvant-shop-purchase"), {"item": "frame-bronze"})
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "purchase_failed"

    def test_anonim_hamyonni_kormaydi(self, catalogue) -> None:
        assert APIClient().get(reverse("qvant-wallet")).status_code in (401, 403)


@pytest.mark.django_db
class TestProfileQuest:
    def test_profil_toldirilganda_quest(self, user, catalogue, fake_s3) -> None:
        """Rasm faqat yuklash orqali qo'yiladi — quest ham o'sha yerda beriladi."""
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.patch(reverse("me"), {"display_name": "Aziz", "bio": "CP ishqibozi"})
        assert r.status_code == 200
        assert ledger.get_wallet(user).balance == 0, "rasmsiz profil hali to'liq emas"

        rasm = SimpleUploadedFile("a.png", b"\x89PNG\r\n\x1a\n" + bytes(64), "image/png")
        r = c.post(reverse("me-avatar"), {"file": rasm}, format="multipart")

        assert r.status_code == 200
        assert ledger.get_wallet(user).balance == 50

    def test_notoliq_profil_quest_bermaydi(self, user, catalogue) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        c.patch(reverse("me"), {"display_name": "Aziz"})
        assert ledger.get_wallet(user).balance == 0


@pytest.mark.django_db
class TestPhasedReveal:
    """ADR-0006 fazali ochilish — API shartnomasi.

    Bu testlar yozilmagani uchun Activity serializerga qo'shilmay qolgan
    edi: kod yozilgan, UI kutgan, API esa bermagan.
    """

    def test_ommaviy_profil_activity_beradi(self, user, catalogue) -> None:
        user.rating_activity = 42
        user.streak_count = 3
        user.save()
        body = APIClient().get(reverse("user-detail", args=[user.username])).json()
        assert body["rating_activity"] == 42
        assert body["streak_count"] == 3

    def test_ommaviy_profil_maydonlari_qulflangan(self, user) -> None:
        """Aniq to'plam — serializer o'zgarsa frontend tipi jim qolmasin.

        `bio` va `avatar_url` serializerda bor edi, apps/web tipida yo'q edi:
        maydon borligini tekshirish bunday siljishni ushlamaydi, to'plam esa
        ushlaydi.
        """
        body = APIClient().get(reverse("user-detail", args=[user.username])).json()
        assert set(body) == {
            "username",
            "display_name",
            "avatar_url",
            "bio",
            # Unvon — ism rangi hamma joyda shundan (ADR-0018).
            "title",
            # Mamlakat — reyting jadvalidagi bayroq uchun (yashirilgan
            # bo'lsa bo'sh satr keladi, maydon esa baribir qoladi).
            "country",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "rating_challenges",
            "streak_count",
            # Stored counters (ADR-0024); `apps/web` has them in `User` too.
            "streak_max",
            "solved_count",
            # CF ladder + social counters (ADR-0026 sync, ADR-0027 tiers).
            # `ProfileCard.tsx` renders all four, so they are part of the
            # public contract — this set is what keeps the web type honest.
            "cf_title",
            "cf_max_title",
            "friend_count",
            "title_photo_url",
            "date_joined",
            "ranks",
            "max_ratings",
            "solved_by_level",
        }

    def test_challenges_endi_beriladi(self, user) -> None:
        """Phase 3 — duel qurildi, reyting ochildi."""
        body = APIClient().get(reverse("user-detail", args=[user.username])).json()
        assert body["rating_challenges"] == 1400

    def test_yashirilgan_mamlakat_bosh_keladi(self, user) -> None:
        """Reyting jadvali OMMAVIY: mamlakatni yashirgan odamda bayroq
        chizilmasligi kerak, ya'ni maydon bo'sh satr bo'lib keladi."""
        user.country = "UZ"
        user.hidden_fields = ["country"]
        user.save()
        body = APIClient().get(reverse("user-detail", args=[user.username])).json()
        assert body["country"] == ""

    def test_ochiq_mamlakat_keladi(self, user) -> None:
        user.country = "UZ"
        user.hidden_fields = []
        user.save()
        body = APIClient().get(reverse("user-detail", args=[user.username])).json()
        assert body["country"] == "UZ"

    def test_me_activity_beradi(self, user) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        body = c.get(reverse("me")).json()
        assert "rating_activity" in body
        assert "streak_count" in body

    def test_reyting_maydonlari_faqat_oqish(self, user) -> None:
        """Reytingni API orqali o'zgartirib bo'lmasligi kerak."""
        c = APIClient()
        c.force_authenticate(user=user)
        c.patch(reverse("me"), {"rating_skills": 99999, "rating_activity": 99999})
        user.refresh_from_db()
        assert user.rating_skills == 0
        assert user.rating_activity == 0


@pytest.mark.django_db
class TestMarathon:
    """PRD P1-9 — haftalik marafon."""

    def _archive(self, n: int) -> None:
        from problems.models import Problem

        for i in range(n):
            Problem.objects.create(
                slug=f"m{i}",
                title=f"M{i}",
                statement="…",
                difficulty=800 + (i % 10) * 100,
                is_public=True,
            )

    def test_kichik_arxivda_marafon_yoq(self, user, catalogue) -> None:
        """Arxiv kichik bo'lsa marafon bo'lmasligi kerak.

        Aks holda bitta masala yechish +100 Qvant berardi.
        """
        from qvant.marathon import marathon_problems

        self._archive(5)
        assert marathon_problems(user) == []

    def test_yetarli_arxivda_marafon_bor(self, user, catalogue) -> None:
        from qvant.marathon import MARATHON_SIZE, marathon_problems

        self._archive(30)
        assert len(marathon_problems(user)) == MARATHON_SIZE

    def test_toplam_barqaror(self, user, catalogue) -> None:
        """To'plam hafta davomida o'zgarmaydi."""
        from qvant.marathon import marathon_problems

        self._archive(30)
        first = [p.pk for p in marathon_problems(user)]
        second = [p.pk for p in marathon_problems(user)]
        assert first == second

    def test_haftalar_farq_qiladi(self, user, catalogue) -> None:
        from datetime import timedelta

        from qvant.marathon import marathon_problems

        self._archive(40)
        today = timezone.localdate()
        this_week = [p.pk for p in marathon_problems(user, today)]
        other = [p.pk for p in marathon_problems(user, today - timedelta(weeks=5))]
        assert this_week != other

    def test_har_kimga_oz_toplami(self, user, other_user, catalogue) -> None:
        """Umumiy to'plamda oldin yechilgan bitta masala butun haftani
        qulflab qo'yardi — o'lchandi: 700 masala yechganning imkoni 1.7 %."""
        from qvant.marathon import marathon_problems

        self._archive(40)
        assert [p.pk for p in marathon_problems(user)] != [
            p.pk for p in marathon_problems(other_user)
        ]

    def test_oldin_yechilgan_masala_toplamga_kirmaydi(self, user, catalogue) -> None:
        from datetime import timedelta

        from problems.models import Problem
        from qvant.marathon import marathon_problems, week_start
        from ratings.models import UserSolvedProblem

        self._archive(30)
        before = marathon_problems(user)
        row = UserSolvedProblem.objects.create(
            user=user, problem=before[0], difficulty_at_solve=before[0].difficulty
        )
        UserSolvedProblem.objects.filter(pk=row.pk).update(
            first_ac_at=timezone.now() - timedelta(days=week_start().weekday() + 8)
        )

        after = marathon_problems(user)

        assert before[0].pk not in {p.pk for p in after}
        assert len(after) == len(before)
        assert Problem.objects.filter(is_public=True).count() == 30

    def test_shu_hafta_yechilgani_toplamdan_chiqmaydi(self, user, catalogue) -> None:
        """To'plam hafta boshiga mahkamlangan: yechish uni o'zgartirmaydi,
        aks holda marafon hech qachon tugamasdi."""
        from qvant.marathon import marathon_problems, solved_this_week
        from ratings.models import UserSolvedProblem

        self._archive(30)
        chosen = marathon_problems(user)
        UserSolvedProblem.objects.create(
            user=user, problem=chosen[0], difficulty_at_solve=chosen[0].difficulty
        )

        assert [p.pk for p in marathon_problems(user)] == [p.pk for p in chosen]
        assert solved_this_week(user) == {chosen[0].pk}

    def test_toliq_yechilganda_mukofot(self, user, catalogue) -> None:
        from judging.models import Attempt
        from problems.models import Language
        from qvant.marathon import check_completion, marathon_problems

        self._archive(12)
        lang = Language.objects.create(code="py", name="Python", run_cmd=["python3"])
        for p in marathon_problems(user):
            a = Attempt.objects.create(user=user, problem=p, language=lang, source_code="x")
            apply_result({"attempt_id": a.pk, "verdict": "AC"})
        # AC lar davomida allaqachon berilgan bo'lishi mumkin
        assert (
            check_completion(user) > 0
            or UserQuestCompletion.objects.filter(user=user, quest__code="weekly_marathon").exists()
        )

    def test_qisman_yechilganda_mukofot_yoq(self, user, catalogue) -> None:
        from judging.models import Attempt
        from problems.models import Language
        from qvant.marathon import check_completion, marathon_problems

        self._archive(20)
        lang = Language.objects.create(code="py", name="Python", run_cmd=["python3"])
        for p in marathon_problems(user)[:3]:
            a = Attempt.objects.create(user=user, problem=p, language=lang, source_code="x")
            apply_result({"attempt_id": a.pk, "verdict": "AC"})
        assert check_completion(user) == 0


@pytest.mark.django_db
class TestRatingHistoryApi:
    """05-domain-model 🔒 dagi endpoint — principle #2 ning ko'rinadigan qismi."""

    def test_tarix_ommaviy(self, user, catalogue, problem, language) -> None:
        from judging.models import Attempt
        from judging.services import apply_result

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})

        body = APIClient().get(reverse("rating-history", args=[user.username])).json()
        skills = [r for r in body["results"] if r["rating_type"] == "skills"]
        assert skills[0]["delta"] == 800
        assert skills[0]["reason"] == "problem_solved"
        assert skills[0]["ref_id"] == problem.slug

    def test_tur_boyicha_filtr(self, user, catalogue, problem, language) -> None:
        from judging.models import Attempt
        from judging.services import apply_result

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        body = (
            APIClient()
            .get(reverse("rating-history", args=[user.username]), {"type": "activity"})
            .json()
        )
        assert all(r["rating_type"] == "activity" for r in body["results"])

    def test_yechilgan_masalalar(self, user, catalogue, problem, language) -> None:
        from judging.models import Attempt
        from judging.services import apply_result

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        body = APIClient().get(reverse("solved-problems", args=[user.username])).json()
        row = body["results"][0]
        assert row["slug"] == problem.slug
        assert row["difficulty"] == row["difficulty_at_solve"] == 800

    def test_qayta_baholangach_farq_korinadi(self, user, catalogue, problem, language) -> None:
        """ADR-0007 auditi: joriy va yechilgandagi qiyinlik farqi ko'rinadi."""
        from judging.models import Attempt
        from judging.services import apply_result
        from ratings.services import recalc_skills_for_problem

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        problem.difficulty = 1500
        problem.save()
        recalc_skills_for_problem(problem.pk)

        row = APIClient().get(reverse("solved-problems", args=[user.username])).json()["results"][0]
        assert row["difficulty"] == 1500
        assert row["difficulty_at_solve"] == 800

    def test_notanish_foydalanuvchi_404(self) -> None:
        assert APIClient().get(reverse("rating-history", args=["yoq"])).status_code == 404


@pytest.mark.django_db
class TestQvantAudit:
    """`verify_balance` bittasini tekshiradi — 10 000 hamyonda farq ko'rinmay qolardi."""

    def audit(self, **kwargs):
        from io import StringIO

        from django.core.management import call_command

        out = StringIO()
        call_command("qvant_audit", stdout=out, **kwargs)
        return out.getvalue()

    def test_mos_kelganda_jim(self, user) -> None:
        ledger.credit(user, 40, QvantTransaction.Reason.ADMIN)

        assert "hammasi mos" in self.audit()

    def test_farqni_topadi_va_tuzatadi(self, user) -> None:
        ledger.credit(user, 40, QvantTransaction.Reason.ADMIN)
        # Ledgerni chetlab yozish — aynan shu holat sinovda uchradi.
        QvantTransaction.objects.create(
            user=user, amount=300, reason=QvantTransaction.Reason.ADMIN, balance_after=0
        )

        report = self.audit()
        assert "farq bor" in report
        assert ledger.get_wallet(user).balance == 40

        self.audit(fix=True)
        # Ledger — haqiqat manbai (ADR-0002), kesh unga moslashadi.
        assert ledger.get_wallet(user).balance == 340


@pytest.mark.django_db(transaction=True)
def test_kunlik_shift_parallel_mukofotda_ham_ushlaydi(user) -> None:
    """ADR-0002 anti-farm: shift qulf OSTIDA hisoblanishi shart.

    Ilgari u qulfdan oldin hisoblanardi va bir vaqtda kelgan sakkizta
    mukofot 100 lik shiftda 400 Qvant bergan edi (jonli o'lchov).
    Bitta foydalanuvchining bir necha yechimi bitta `drain_results`
    partiyasida tekshirilsa, mukofotlar aynan shunday keladi.
    """
    import threading

    from django.db import connection, connections

    # SQLite `select_for_update` ni qo'llab-quvvatlamaydi («table is
    # locked»). CI Postgres'da ishlaydi, ya'ni sinov o'sha yerda haqiqiy.
    if connection.vendor != "postgresql":
        pytest.skip("qulf semantikasi faqat Postgres'da tekshiriladi")

    barrier = threading.Barrier(6)

    def award():
        try:
            barrier.wait()
            ledger.credit(user, 50, QvantTransaction.Reason.QUEST)
        finally:
            connections.close_all()

    threads = [threading.Thread(target=award) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert ledger.earned_today(user) == DAILY_EARN_CAP
    assert ledger.get_wallet(user).balance == DAILY_EARN_CAP


@pytest.mark.django_db
class TestRejudgeQaytarish:
    """Rejudge AC ni yiqitganda Qvant qaytarilishi — ADR-0002.

    Ilgari `revoke_for_attempt` `ref_type="attempt"` bo'yicha qidirardi,
    lekin hech qayerda shunday havola bilan Qvant berilmasdi: o'lchandi —
    rejudge'dan keyin skills 800→0, solved_count 1→0, Qvant esa 10 da
    qolardi.
    """

    def _solve(self, user, problem, language):
        from judging.models import Attempt
        from qvant.services import on_first_accepted
        from ratings.services import on_attempt_judged

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x", verdict="AC"
        )
        on_attempt_judged(attempt)
        on_first_accepted(user)
        return attempt

    def _revoke(self, attempt):
        from judging.models import Attempt
        from ratings.services import on_accept_revoked

        Attempt.objects.filter(pk=attempt.pk).update(verdict="WA")
        attempt.refresh_from_db()
        on_accept_revoked(attempt)

    def test_yagona_ac_yiqilsa_pul_qaytariladi(self, user, problem, language) -> None:
        quests.sync_catalogue()
        attempt = self._solve(user, problem, language)
        assert ledger.get_wallet(user).balance == 20  # daily_solve + «birinchi masala» yutug'i

        self._revoke(attempt)

        # Ikkalasi ham qaytariladi (ADR-0002: rejudge da qaytarish).
        assert ledger.get_wallet(user).balance == 0
        assert not UserAchievement.objects.filter(user=user).exists()
        assert not UserQuestCompletion.objects.filter(
            user=user, quest__code=quests.DAILY_SOLVE
        ).exists()
        # Streak ataylab tegilmaydi — rejudge bizning xatomiz.
        user.refresh_from_db()
        assert user.streak_count == 1

    def test_kunda_boshqa_yechim_qolsa_pul_qolaveradi(self, user, problem, language) -> None:
        """Quest kunga bog'langan: bitta AC yiqilsa ham mukofot haqli."""
        quests.sync_catalogue()
        second = type(problem).objects.create(
            slug="ikkinchi", title="Ikkinchi", statement="…", difficulty=1000, is_public=True
        )
        attempt = self._solve(user, problem, language)
        self._solve(user, second, language)
        balance = ledger.get_wallet(user).balance

        self._revoke(attempt)

        assert ledger.get_wallet(user).balance == balance
        assert UserQuestCompletion.objects.filter(
            user=user, quest__code=quests.DAILY_SOLVE
        ).exists()

    def test_uchtalik_quest_shart_buzilganda_qaytariladi(self, user, problem, language) -> None:
        quests.sync_catalogue()
        extra = [
            type(problem).objects.create(
                slug=f"qoshimcha-{i}",
                title=f"Q{i}",
                statement="…",
                difficulty=1000,
                is_public=True,
            )
            for i in range(2)
        ]
        self._solve(user, problem, language)
        self._solve(user, extra[0], language)
        last = self._solve(user, extra[1], language)
        assert ledger.get_wallet(user).balance == 35  # daily_solve, daily_three_ac, solve-1

        self._revoke(last)

        # 3→2: uchtalik quest yiqildi; kunlik quest va «birinchi masala» yutug'i qoldi.
        assert ledger.get_wallet(user).balance == 20
        assert not UserQuestCompletion.objects.filter(
            user=user, quest__code=quests.DAILY_THREE_AC
        ).exists()


@pytest.mark.django_db(transaction=True)
def test_takrorlanmas_narsa_parallel_xaridda_bir_marta_sotiladi(user) -> None:
    """`exists()` bilan `debit()` orasidagi oyna — o'lchandi.

    `UserInventory` da uniq cheklov yo'q (streak freeze takroriy sotib
    olinadi), shuning uchun tekshiruv poygaga ochiq edi: 6 ta parallel
    so'rov ramkani 4 marta sotib, 100 o'rniga 400 Qvant yechgan.
    """
    import threading

    from django.db import connection, connections

    if connection.vendor != "postgresql":
        pytest.skip("qulf semantikasi faqat Postgres'da tekshiriladi")

    item = ShopItem.objects.create(
        code="ramka",
        category=ShopItem.Category.AVATAR_FRAME,
        title_uz="Ramka",
        price=100,
        is_consumable=False,
    )
    ledger.credit(user, 600, QvantTransaction.Reason.ADMIN)

    barrier = threading.Barrier(6)
    ok = []

    def buy():
        try:
            barrier.wait()
            purchase(user, item.code)
            ok.append(1)
        except PurchaseError:
            pass
        finally:
            connections.close_all()

    threads = [threading.Thread(target=buy) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(ok) == 1
    assert UserInventory.objects.filter(user=user, item=item).count() == 1
    assert ledger.get_wallet(user).balance == 500


@pytest.mark.django_db
def test_takroriy_narsa_qulfdan_keyin_ham_qayta_sotiladi(user) -> None:
    """Qulf streak freeze kabi consumable narsani bloklab qo'ymasligi kerak."""
    item = ShopItem.objects.create(
        code="muzlatgich",
        category=ShopItem.Category.STREAK_FREEZE,
        title_uz="Freeze",
        price=50,
        is_consumable=True,
    )
    ledger.credit(user, 200, QvantTransaction.Reason.ADMIN)

    purchase(user, item.code)
    purchase(user, item.code)

    assert UserInventory.objects.filter(user=user, item=item).count() == 2


@pytest.mark.django_db
def test_marafon_endpointi_toplamni_va_progressni_beradi(user, catalogue) -> None:
    """Marafon ilgari hech qayerda ko'rinmasdi — foydalanuvchi qaysi
    masalalarni yechish kerakligini bilolmasdi."""
    from problems.models import Problem
    from qvant.marathon import MARATHON_REWARD, MARATHON_SIZE, marathon_problems
    from ratings.models import UserSolvedProblem

    for i in range(30):
        Problem.objects.create(
            slug=f"mm{i}", title=f"MM{i}", statement="…", difficulty=800, is_public=True
        )
    chosen = marathon_problems(user)
    UserSolvedProblem.objects.create(
        user=user, problem=chosen[0], difficulty_at_solve=chosen[0].difficulty
    )

    c = APIClient()
    c.force_authenticate(user=user)
    body = c.get(reverse("qvant-marathon")).json()

    assert body["total"] == MARATHON_SIZE
    assert body["reward"] == MARATHON_REWARD
    assert body["solved_count"] == 1
    assert body["completed"] is False
    assert [p["slug"] for p in body["problems"]] == [p.slug for p in chosen]
    assert [p["marathon_solved"] for p in body["problems"]].count(True) == 1


@pytest.mark.django_db
def test_marafon_endpointi_kirishni_talab_qiladi() -> None:
    assert APIClient().get(reverse("qvant-marathon")).status_code == 401
