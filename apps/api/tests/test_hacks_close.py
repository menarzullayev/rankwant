"""Hack oynasining yopilishi va reyting bilan bog'lanishi — ADR-0020, 7-tamoyil.

Tartib shu yerda sinaladi: testlar qo'shiladi → `AC` lar qayta
tekshiriladi → SHUNDAN KEYIN reyting. Tartib buzilsa, hack qilingan
yechim reytingga to'g'ri deb kirib ketardi va uni qaytarish reyting
tarixini buzardi.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from contests.models import Contest, Standing
from contests.services import finalize_contest, rebuild_standings
from core.models import User
from hacks import policies
from hacks.models import Hack
from hacks.policies import Policy
from hacks.services import close_hack_phase, hack_phase_pending
from hacks.tasks import close_due, reap_stuck
from judging.models import Attempt
from judging.verdicts import Verdict
from notifications.models import Notification
from problems.models import TestCase


@pytest.fixture(autouse=True)
def fake_storage(fake_hack_storage: dict[str, str]) -> dict[str, str]:
    return fake_hack_storage


@pytest.fixture
def room_contest(contest: Contest) -> Contest:
    """Tugagan, xona hackingi yoqilgan musobaqa — oyna `end_at` da yopiladi."""
    contest.hack_room = True
    contest.save(update_fields=["hack_room"])
    return contest


def _hack(
    contest: Contest,
    attempt: Attempt,
    hacker: User,
    *,
    policy: Policy = policies.CONTEST_ROOM,
    status: str = Hack.Status.SUCCESSFUL,
) -> Hack:
    """Yakunlangan hack — bu yerda uch bosqichli oqim sinalmaydi."""
    return Hack.objects.create(
        hacker=hacker,
        defender_attempt=attempt,
        problem=attempt.problem,
        contest=contest,
        policy=policy.code,
        status=status,
        stage=Hack.Stage.DONE if status != Hack.Status.TESTING else Hack.Stage.DEFEND,
        points=policy.success_points if status == Hack.Status.SUCCESSFUL else 0,
        input_ref="s3://test/hacks/1.in",
        output_ref="s3://test/hacks/1.out",
        judged_at=timezone.now() if status != Hack.Status.TESTING else None,
    )


def _in_contest(attempt: Attempt, contest: Contest) -> Attempt:
    """Urinishni musobaqa oynasiga ko'chiradi.

    `created_at` — `auto_now_add`, ya'ni `save()` bilan o'zgarmaydi;
    jadval esa faqat `end_at` dan oldingi urinishlarni oladi.
    """
    Attempt.objects.filter(pk=attempt.pk).update(
        contest=contest, created_at=contest.start_at + timedelta(minutes=5)
    )
    attempt.refresh_from_db()
    return attempt


@pytest.mark.django_db
class TestClosePhase:
    def test_test_qoshiladi_va_ac_lar_qayta_yuboriladi(
        self, room_contest, defender_attempt, user, memory_judge
    ) -> None:
        _in_contest(defender_attempt, room_contest)
        _hack(room_contest, defender_attempt, user)

        added = close_hack_phase(room_contest)
        room_contest.refresh_from_db()
        defender_attempt.refresh_from_db()

        assert added == 1
        assert TestCase.objects.filter(origin=TestCase.Origin.HACK).count() == 1
        assert room_contest.hack_tests_added_at is not None
        assert room_contest.hack_phase_closed_at is not None
        # `AC` yangi test bilan qayta tekshiriladi — `PENDING` EMAS:
        # foydalanuvchi eski natija bekor qilinganini ko'rishi kerak.
        assert defender_attempt.verdict == Verdict.TESTING_ABORTED
        assert [j.attempt_id for j in memory_judge.jobs] == [defender_attempt.pk]

    def test_ikkinchi_yopish_hech_narsa_qilmaydi(
        self, room_contest, defender_attempt, user
    ) -> None:
        """Beat har daqiqada chaqiradi — ikki chaqiruv ustma-ust tushishi mumkin."""
        _in_contest(defender_attempt, room_contest)
        _hack(room_contest, defender_attempt, user)

        assert close_hack_phase(room_contest) == 1
        assert close_hack_phase(room_contest) == 0
        assert TestCase.objects.filter(origin=TestCase.Origin.HACK).count() == 1

    def test_darhol_qoshiladigan_siyosat_bu_yerda_qoshilmaydi(
        self, room_contest, defender_attempt, user
    ) -> None:
        """Uphack testi allaqachon qo'shilgan (`IMMEDIATE`) — takrorlanmasin."""
        _in_contest(defender_attempt, room_contest)
        _hack(room_contest, defender_attempt, user, policy=policies.UPHACK)

        assert close_hack_phase(room_contest) == 0
        assert not TestCase.objects.filter(origin=TestCase.Origin.HACK).exists()


@pytest.mark.django_db
class TestCloseDue:
    def test_ochiq_faza_ketayotganda_kutiladi(self, contest, defender_attempt, user) -> None:
        contest.hack_open_minutes = 60
        contest.save(update_fields=["hack_open_minutes"])

        assert close_due() == 0
        contest.refresh_from_db()
        assert contest.hack_phase_closed_at is None

    def test_tekshirilayotgan_hack_kutiladi(self, room_contest, defender_attempt, user) -> None:
        """Javobi kelmagan hack testi to'plamga tushmay qolib ketmasin."""
        _in_contest(defender_attempt, room_contest)
        _hack(room_contest, defender_attempt, user, status=Hack.Status.TESTING)

        assert close_due() == 0
        room_contest.refresh_from_db()
        assert room_contest.hack_phase_closed_at is None

    def test_oyna_yopilgach_faza_yopiladi(self, room_contest, defender_attempt, user) -> None:
        _in_contest(defender_attempt, room_contest)
        _hack(room_contest, defender_attempt, user)

        assert close_due() == 1
        room_contest.refresh_from_db()
        assert room_contest.hack_phase_closed_at is not None

    def test_hacksiz_musobaqa_tegilmaydi(self, contest) -> None:
        """Hack yoqilmagan musobaqa bu vazifaning ishi emas."""
        assert close_due() == 0
        contest.refresh_from_db()
        assert contest.hack_phase_closed_at is None


@pytest.mark.django_db
class TestRatingWaits:
    def test_faza_yopilmaguncha_reyting_qollanmaydi(self, room_contest) -> None:
        assert hack_phase_pending(room_contest) is True
        assert finalize_contest(room_contest) == 0

        room_contest.refresh_from_db()
        assert room_contest.ratings_applied_at is None

    def test_qayta_tekshiruv_tugamaguncha_ham_kutiladi(
        self, room_contest, defender_attempt, user
    ) -> None:
        """Faza yopildi, lekin natijalar hali kelmadi.

        Shu oraliqda reyting hisoblansa, bekor qilinishi kerak bo'lgan
        `AC` unga kirib ketardi.
        """
        _in_contest(defender_attempt, room_contest)
        _hack(room_contest, defender_attempt, user)
        close_hack_phase(room_contest)
        room_contest.refresh_from_db()

        assert hack_phase_pending(room_contest) is True
        assert finalize_contest(room_contest) == 0

    def test_hammasi_tugagach_yakunlanadi(self, room_contest, defender_attempt, user) -> None:
        _in_contest(defender_attempt, room_contest)
        close_hack_phase(room_contest)
        room_contest.refresh_from_db()

        assert hack_phase_pending(room_contest) is False
        finalize_contest(room_contest)

        room_contest.refresh_from_db()
        assert room_contest.ratings_applied_at is not None

    def test_hacksiz_musobaqa_kutmaydi(self, contest) -> None:
        assert hack_phase_pending(contest) is False


@pytest.mark.django_db
class TestStandings:
    def test_hack_bali_ioi_jadvalida(self, contest, defender_attempt, user, other_user) -> None:
        """IOI ballli — Codeforces modelidagi kabi hack bali tartibga kiradi."""
        contest.scoring_type = Contest.Scoring.IOI
        contest.hack_room = True
        contest.save(update_fields=["scoring_type", "hack_room"])
        _in_contest(defender_attempt, contest)
        _hack(contest, defender_attempt, user)

        rebuild_standings(contest)

        hacker = Standing.objects.get(contest=contest, user=user)
        assert hacker.hack_score == 100
        assert hacker.hacks_successful == 1
        assert hacker.total_score == 100
        # Urinishi bo'lmasa ham jadvalga tushdi va birinchi o'rinda
        assert hacker.rank == 1

    def test_muvaffaqiyatsiz_hack_ball_yeydi(self, contest, defender_attempt, user) -> None:
        contest.scoring_type = Contest.Scoring.IOI
        contest.hack_room = True
        contest.save(update_fields=["scoring_type", "hack_room"])
        _in_contest(defender_attempt, contest)
        _hack(contest, defender_attempt, user, status=Hack.Status.UNSUCCESSFUL)
        Hack.objects.update(points=policies.CONTEST_ROOM.failure_points)

        rebuild_standings(contest)

        hacker = Standing.objects.get(contest=contest, user=user)
        assert hacker.hack_score == -50
        assert hacker.hacks_unsuccessful == 1
        # Musbat maydon nolga qisiladi, haqiqiy ball ustunda ko'rinadi
        assert hacker.total_score == 0

    def test_uphack_jadvalni_ozgartirmaydi(self, contest, defender_attempt, user) -> None:
        """Reyting allaqachon tarqalgan — jadval qayta yozilmaydi (ADR-0020)."""
        _in_contest(defender_attempt, contest)
        _hack(contest, defender_attempt, user, policy=policies.UPHACK)

        rebuild_standings(contest)

        assert not Standing.objects.filter(contest=contest, user=user).exists()


@pytest.mark.django_db
class TestReapStuck:
    def test_javobsiz_hack_hisobga_olinmaydi(self, room_contest, defender_attempt, user) -> None:
        hack = _hack(room_contest, defender_attempt, user, status=Hack.Status.TESTING)
        # `updated_at` — `auto_now`, ya'ni `save()` uni qaytarib yozardi.
        Hack.objects.filter(pk=hack.pk).update(updated_at=timezone.now() - timedelta(hours=1))

        assert reap_stuck() == 1

        hack.refresh_from_db()
        assert hack.status == Hack.Status.IGNORED
        assert hack.points == 0
        # Hacker nima bo'lganini biladi — jim yo'qolish emas
        assert Notification.objects.filter(user=user, kind=Notification.Kind.HACK).exists()

    def test_yangi_hack_tegilmaydi(self, room_contest, defender_attempt, user) -> None:
        _hack(room_contest, defender_attempt, user, status=Hack.Status.TESTING)

        assert reap_stuck() == 0
