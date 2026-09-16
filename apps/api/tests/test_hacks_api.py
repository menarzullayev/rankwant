"""Hack API — ADR-0020 ning tashqi yuzasi.

Dvigatelning o'zi `test_hacks.py` da sinaladi. Bu yerda faqat qatlamning
O'Z mas'uliyati: ruxsat, kiritma tekshiruvi, ko'rinish qoidasi, lock va
tezlik chegarasi. Ular dvigatelda yo'q va faqat HTTP orqali ko'rinadi.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from contests.models import Contest, ContestRegistration
from core.models import User
from core.throttling import ResilientScopedRateThrottle
from hacks.models import Hack, HackLock
from hacks.services import submit
from judging.models import Attempt
from judging.verdicts import Verdict


@pytest.fixture
def one_hack_per_minute(monkeypatch: pytest.MonkeyPatch) -> None:
    """`hack` shiftini bitta so'rovga tushiradi.

    `override_settings(REST_FRAMEWORK=...)` bu yerda ISHLAMAYDI: DRF
    `SimpleRateThrottle.THROTTLE_RATES` ni SINF e'lon qilinayotganda bir
    marta bog'laydi, ya'ni sozlama almashtirilgach ham throttle eski
    lug'atga qarayveradi. O'lchandi: shift umuman urilmadi va ikkinchi
    so'rov 429 o'rniga 400 («allaqachon tekshirilmoqda») qaytardi —
    ya'ni test yashil bo'lib, himoyani sinamagan bo'lardi.
    """
    monkeypatch.setattr(ResilientScopedRateThrottle, "THROTTLE_RATES", {"hack": "1/min"})


@pytest.fixture(autouse=True)
def fake_storage(fake_hack_storage: dict[str, str]) -> dict[str, str]:
    """Butun modulda S3 o'rniga lug'at."""
    return fake_hack_storage


@pytest.fixture
def room_contest(contest: Contest) -> Contest:
    """Xona hackingi yoqilgan va HOZIR ketayotgan musobaqa."""
    now = timezone.now()
    contest.hack_room = True
    contest.start_at = now - timedelta(hours=1)
    contest.end_at = now + timedelta(hours=1)
    contest.save(update_fields=["hack_room", "start_at", "end_at"])
    return contest


def _client(user: User | None = None) -> APIClient:
    client = APIClient()
    if user is not None:
        client.force_authenticate(user=user)
    return client


def _payload(attempt: Attempt, **extra: object) -> dict[str, object]:
    return {"attempt": attempt.pk, "test_input": "1 2\n", **extra}


@pytest.mark.django_db
class TestSubmitEndpoint:
    def test_kirmagan_foydalanuvchi_yubora_olmaydi(self, defender_attempt) -> None:
        r = _client().post(reverse("hack-list"), _payload(defender_attempt), format="json")
        assert r.status_code in (401, 403)
        assert not Hack.objects.exists()

    def test_yuborish_navbatga_tushadi(self, defender_attempt, user, memory_judge) -> None:
        r = _client(user).post(reverse("hack-list"), _payload(defender_attempt), format="json")

        assert r.status_code == 201, r.content
        hack = Hack.objects.get(pk=r.json()["id"])
        assert hack.status == Hack.Status.TESTING
        assert hack.stage == Hack.Stage.REFERENCE
        # Marshrutlash maydonlari ishga YOZILGAN bo'lishi shart: ularsiz
        # natija qaytganda uni hech kim hack bilan bog'lay olmasdi.
        assert [(j.hack_id, j.hack_stage) for j in memory_judge.jobs] == [
            (hack.pk, Hack.Stage.REFERENCE)
        ]

    def test_dvigatel_rad_etsa_sabab_qaytadi(self, defender_attempt, other_user) -> None:
        """Himoyachining o'zi — rad etish sababi bilan, 500 emas."""
        r = _client(other_user).post(
            reverse("hack-list"), _payload(defender_attempt), format="json"
        )

        assert r.status_code == 400
        body = r.json()["error"]
        assert body["code"] == "hack_rejected"
        assert "O'z yechimingizni" in body["message"]

    def test_kiritma_ham_generator_ham_bolmasa(self, defender_attempt, user) -> None:
        r = _client(user).post(
            reverse("hack-list"), {"attempt": defender_attempt.pk}, format="json"
        )
        assert r.status_code == 400

    def test_ikkalasi_birga_berilsa_rad_etiladi(self, defender_attempt, user, language) -> None:
        """Ikki manba — qaysi biri ishlatilgani noaniq bo'lardi."""
        r = _client(user).post(
            reverse("hack-list"),
            _payload(defender_attempt, generator_language=language.code, generator_source="x"),
            format="json",
        )
        assert r.status_code == 400

    def test_notanish_urinish_400_beradi(self, user) -> None:
        """Raqam bo'lmagan `attempt` ham 500 EMAS: `pk=` ga xom satr
        berilsa `ValueError` chiqardi."""
        r = _client(user).post(
            reverse("hack-list"), {"attempt": "abc", "test_input": "1\n"}, format="json"
        )
        assert r.status_code == 400

    def test_kiritmaning_oxirgi_qatori_saqlanadi(
        self, defender_attempt, user, fake_hack_storage
    ) -> None:
        """DRF standart holatda bo'sh belgilarni qirqadi.

        Test kiritmasida oxirgi qator uzilishi ma'noga ega: qirqilgan
        kiritma bilan etalon yechim boshqa javob berib, hack sababsiz
        «ishlamagan» bo'lib chiqardi.
        """
        r = _client(user).post(
            reverse("hack-list"),
            {"attempt": defender_attempt.pk, "test_input": "1 2\n\n"},
            format="json",
        )

        assert r.status_code == 201
        assert list(fake_hack_storage.values()) == ["1 2\n\n"]

    @override_settings(HACK_INPUT_MAX_BYTES=8)
    def test_katta_kiritma_rad_etiladi(self, defender_attempt, user) -> None:
        r = _client(user).post(
            reverse("hack-list"),
            {"attempt": defender_attempt.pk, "test_input": "x" * 64},
            format="json",
        )
        assert r.status_code == 400
        assert not Hack.objects.exists()


@pytest.mark.django_db
class TestVisibility:
    def test_hackning_materiali_faqat_egasiga(self, defender_attempt, user, other_user) -> None:
        """Generator manbasi va kiritma — hackerning o'z mehnati.

        Ommaviy bo'lsa, hack yuborish o'z kodini e'lon qilish bilan
        barobar bo'lardi; natijaning o'zi esa ochiq qoladi.
        """
        hack = submit(user, defender_attempt, raw_input="1 2\n")
        hack.detail = "validator: n juda katta"
        hack.save(update_fields=["detail"])
        url = reverse("hack-detail", args=[hack.pk])

        mine = _client(user).get(url).json()
        assert mine["detail"] == "validator: n juda katta"
        assert mine["test_input"] == "1 2\n"

        stranger = _client(other_user).get(url).json()
        assert stranger["detail"] == ""
        assert stranger["test_input"] == ""
        # Natijaning o'zi esa yashirilmaydi
        assert stranger["status"] == Hack.Status.TESTING
        assert stranger["defender"] == other_user.username

    def test_huquqli_hacker_manba_kodini_koradi(self, defender_attempt, user) -> None:
        """ADR-0020, 2-tamoyil: hack qilish uchun kodni ko'rish SHART."""
        url = reverse("attempt-detail", args=[defender_attempt.pk])

        assert _client(user).get(url).json()["source_code"] == "hacked_code"

    def test_begona_manba_kodini_kormaydi(self, defender_attempt) -> None:
        """Istisno NUQTALI: masalani yechmagan odam uchun yopiq qoladi."""
        stranger = User.objects.create_user(username="dilnoza", password="Parol!12345")
        url = reverse("attempt-detail", args=[defender_attempt.pk])

        assert "source_code" not in _client(stranger).get(url).json()
        assert "source_code" not in _client().get(url).json()


@pytest.mark.django_db
class TestEligibilityEndpoint:
    def test_huquqli_foydalanuvchi(self, defender_attempt, user) -> None:
        body = (
            _client(user).get(reverse("hack-eligibility"), {"attempt": defender_attempt.pk}).json()
        )
        assert body == {
            "can_hack": True,
            "reason": "",
            "policy": "practice",
            "policy_label": "Amaliyot",
            "needs_lock": False,
            "locked": False,
        }

    def test_sabab_har_doim_korsatiladi(self, defender_attempt, other_user) -> None:
        body = (
            _client(other_user)
            .get(reverse("hack-eligibility"), {"attempt": defender_attempt.pk})
            .json()
        )
        assert body["can_hack"] is False
        assert "O'z yechimingizni" in body["reason"]

    def test_yopiq_oyna(self, defender_attempt, contest, user) -> None:
        contest.uphack_days = 0
        contest.save(update_fields=["uphack_days"])
        defender_attempt.contest = contest
        defender_attempt.save(update_fields=["contest"])

        body = (
            _client(user).get(reverse("hack-eligibility"), {"attempt": defender_attempt.pk}).json()
        )
        assert body["can_hack"] is False
        assert body["policy"] is None


@pytest.mark.django_db
class TestLock:
    def test_yechmasdan_lock_qilib_bolmaydi(self, room_contest, problem, user) -> None:
        """Lock — o'z ballini xatarga qo'yish; ball bo'lmasa xatar ham yo'q."""
        ContestRegistration.objects.create(contest=room_contest, user=user)

        r = _client(user).post(
            reverse("hacklock-list"),
            {"contest": room_contest.slug, "problem": problem.slug},
            format="json",
        )
        assert r.status_code == 400
        assert "yeching" in r.json()["error"]["message"]
        assert not HackLock.objects.exists()

    def test_lock_qilingach_qayta_yuborib_bolmaydi(
        self, room_contest, problem, language, user
    ) -> None:
        """Qoida API'da turishi SHART.

        Frontendda tugmani o'chirish yetarli emas: lock qilgan odam
        mijoz orqali yechimini jimgina almashtirib, xonadagilarni
        aldagan bo'lardi.
        """
        ContestRegistration.objects.create(contest=room_contest, user=user)
        Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            contest=room_contest,
            source_code="ok",
            verdict=Verdict.AC,
            judged_at=timezone.now(),
        )
        client = _client(user)

        locked = client.post(
            reverse("hacklock-list"),
            {"contest": room_contest.slug, "problem": problem.slug},
            format="json",
        )
        assert locked.status_code == 201, locked.content

        again = client.post(
            reverse("attempt-list"),
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": "int main(){}",
                "contest": room_contest.slug,
            },
            format="json",
        )
        assert again.status_code == 400
        assert "lock" in str(again.json()).lower()

    def test_boshqaning_locklari_korinmaydi(self, room_contest, problem, user, other_user) -> None:
        """Raqib qaysi masalani lock qilgani — taktik ma'lumot."""
        HackLock.objects.create(contest=room_contest, problem=problem, user=other_user)

        r = _client(user).get(reverse("hacklock-list"))
        assert r.status_code == 200
        assert r.json()["results"] == []


@pytest.mark.django_db
class TestRoom:
    def test_royxatdan_otmagan_xona_olmaydi(self, room_contest, user) -> None:
        r = _client(user).get(reverse("hack-room"), {"contest": room_contest.slug})
        assert r.status_code == 400

    def test_xona_birinchi_sorovda_taqsimlanadi(self, room_contest, user, other_user) -> None:
        for participant in (user, other_user):
            ContestRegistration.objects.create(contest=room_contest, user=participant)

        body = _client(user).get(reverse("hack-room"), {"contest": room_contest.slug}).json()
        assert body["number"] == 1
        assert body["members"] == [user.username]

        # Ikkinchi ishtirokchi ham O'SHA xonaga tushadi (chegara 40)
        other = _client(other_user).get(reverse("hack-room"), {"contest": room_contest.slug})
        assert other.json()["number"] == 1


@pytest.mark.django_db
class TestRateLimit:
    def test_shift_urilsa_korinadigan_qator_qoladi(
        self, defender_attempt, user, one_hack_per_minute
    ) -> None:
        """Jim 429 EMAS — `Attempt.RATE_LIMITED` pretsedenti.

        Bitta portlash bitta qator qoldiradi: aks holda rad etilgan
        so'rovlarning o'zi bazani to'ldirish yo'li bo'lardi.
        """
        client = _client(user)
        first = client.post(reverse("hack-list"), _payload(defender_attempt), "json")
        assert first.status_code == 201, first.content
        for _ in range(3):
            throttled = client.post(reverse("hack-list"), _payload(defender_attempt), "json")

        assert throttled.status_code == 429
        assert Hack.objects.filter(hacker=user, status=Hack.Status.RATE_LIMITED).count() == 1
