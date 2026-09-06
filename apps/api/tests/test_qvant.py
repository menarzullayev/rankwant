"""Qvant ledgeri, questlar, streak, do'kon va Activity reyting.

DoD: Qvant ledgerida qamrov MAJBURIY.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from judging.models import Attempt
from judging.services import apply_result
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
        assert QvantWallet.objects.get(user=user).balance == 10  # bitta daily_solve

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
    def test_profil_toldirilganda_quest(self, user, catalogue) -> None:
        c = APIClient()
        c.force_authenticate(user=user)
        r = c.patch(
            reverse("me"),
            {
                "display_name": "Aziz",
                "bio": "CP ishqibozi",
                "avatar_url": "https://example.com/a.png",
            },
        )
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
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "streak_count",
            "date_joined",
        }

    def test_challenges_hali_berilmaydi(self, user) -> None:
        """Phase 3 — duels yo'q, ya'ni qiymat ma'nosiz."""
        body = APIClient().get(reverse("user-detail", args=[user.username])).json()
        assert "rating_challenges" not in body

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

    def test_kichik_arxivda_marafon_yoq(self, db, catalogue) -> None:
        """Arxiv kichik bo'lsa marafon bo'lmasligi kerak.

        Aks holda bitta masala yechish +100 Qvant berardi.
        """
        from qvant.marathon import marathon_problems

        self._archive(5)
        assert marathon_problems() == []

    def test_yetarli_arxivda_marafon_bor(self, db, catalogue) -> None:
        from qvant.marathon import MARATHON_SIZE, marathon_problems

        self._archive(30)
        assert len(marathon_problems()) == MARATHON_SIZE

    def test_toplam_barqaror(self, db, catalogue) -> None:
        """Bir haftada hamma bir xil to'plamni ko'radi."""
        from qvant.marathon import marathon_problems

        self._archive(30)
        first = [p.pk for p in marathon_problems()]
        second = [p.pk for p in marathon_problems()]
        assert first == second

    def test_haftalar_farq_qiladi(self, db, catalogue) -> None:
        from datetime import timedelta

        from qvant.marathon import marathon_problems

        self._archive(40)
        today = timezone.localdate()
        this_week = [p.pk for p in marathon_problems(today)]
        other = [p.pk for p in marathon_problems(today - timedelta(weeks=5))]
        assert this_week != other

    def test_toliq_yechilganda_mukofot(self, user, catalogue) -> None:
        from judging.models import Attempt
        from problems.models import Language
        from qvant.marathon import check_completion, marathon_problems

        self._archive(12)
        lang = Language.objects.create(code="py", name="Python", run_cmd=["python3"])
        for p in marathon_problems():
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
        for p in marathon_problems()[:3]:
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
