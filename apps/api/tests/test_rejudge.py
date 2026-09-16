"""Rejudge — partiyada qayta tekshirish (10-operations § 3)."""

from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Problem
from ratings.models import UserSolvedProblem
from ratings.services import on_accept_revoked, on_attempt_judged


def ac(user, problem, language) -> Attempt:
    a = Attempt.objects.create(
        user=user, problem=problem, language=language, source_code="x", verdict=Verdict.AC
    )
    on_attempt_judged(a)
    return a


@pytest.mark.django_db
class TestAcBekorQilinganda:
    def test_yagona_ac_bekor_qilinsa_yechim_ochadi(self, user, problem, language) -> None:
        a = ac(user, problem, language)

        a.verdict = Verdict.WA
        a.save(update_fields=["verdict"])
        on_accept_revoked(a)

        assert not UserSolvedProblem.objects.filter(user=user, problem=problem).exists()
        assert Problem.objects.get(pk=problem.pk).solved_count == 0

    def test_sanoq_nol_bolsa_ham_bekor_qilish_yiqilmaydi(self, user, problem, language) -> None:
        """Sanoq qatorlardan ajralib ketgan holat.

        `solved_count` — musbat maydon, ya'ni noldan kamaytirish CHECK
        xatosi berib BUTUN tranzaksiyani yiqitardi. Bekor qilishni hack
        dvigateli ham chaqiradi (`hacks.services._finish`), demak begona
        sabab hackni abadiy `TESTING` da qoldirardi.

        Drift o'zi qanday paydo bo'ladi: `UserSolvedProblem` kodni
        chetlab yo'qolganda — foydalanuvchi o'chirilishi (kaskad),
        import yoki qo'lda tuzatish.
        """
        a = ac(user, problem, language)
        Problem.objects.filter(pk=problem.pk).update(solved_count=0)

        a.verdict = Verdict.WA
        a.save(update_fields=["verdict"])
        on_accept_revoked(a)  # yiqilmasligi SHART

        assert Problem.objects.get(pk=problem.pk).solved_count == 0
        assert not UserSolvedProblem.objects.filter(user=user, problem=problem).exists()

    def test_ikkinchi_ac_qolsa_yechim_qoladi(self, user, problem, language) -> None:
        """Bir masalaga bir necha AC odatiy: odam yechimni optimallashtiradi.

        Rejudge faqat BIRINCHISINI yiqitsa (masalan checker qattiqlashdi),
        foydalanuvchida hali ham AC yechim bor — ya'ni masala yechilgan.
        """
        birinchi = ac(user, problem, language)
        ikkinchi = ac(user, problem, language)
        assert ikkinchi.verdict == Verdict.AC

        birinchi.verdict = Verdict.WA
        birinchi.save(update_fields=["verdict"])
        on_accept_revoked(birinchi)

        row = UserSolvedProblem.objects.filter(user=user, problem=problem).first()
        assert row is not None, "hali AC urinishi bor — masala yechilgan bo'lib qolishi kerak"
        assert row.first_ac_attempt_id == ikkinchi.pk
        assert Problem.objects.get(pk=problem.pk).solved_count == 1


@pytest.mark.django_db
class TestRejudgeBuyrugi:
    def test_filtrsiz_ishlamaydi(self) -> None:
        """Filtrsiz rejudge butun arxivni navbatga tiqardi."""
        with pytest.raises(CommandError):
            call_command("rejudge")

    def test_navbatga_qoyadi_va_verdictni_tozalaydi(
        self, user, problem, language, memory_judge
    ) -> None:
        a = ac(user, problem, language)

        call_command("rejudge", problem=problem.slug)

        assert len(memory_judge.jobs) == 1
        assert memory_judge.jobs[0].attempt_id == a.pk
        a.refresh_from_db()
        # `PENDING` emas — pastdagi `TestOlikVerdiktlar` ga qarang.
        assert a.verdict == Verdict.TESTING_ABORTED
        assert a.judged_at is None

    def test_dry_run_hech_narsa_yubormaydi(self, user, problem, language, memory_judge) -> None:
        ac(user, problem, language)

        call_command("rejudge", problem=problem.slug, dry_run=True)

        assert memory_judge.jobs == []

    def test_kutayotgan_urinishga_tegmaydi(self, user, problem, language, memory_judge) -> None:
        """PENDING — `reap_stuck` ning ishi, rejudge niki emas."""
        Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="x",
            verdict=Verdict.PENDING,
        )

        call_command("rejudge", problem=problem.slug)

        assert memory_judge.jobs == []

    def test_urinishlar_sanogi_oshmaydi(self, user, problem, language, memory_judge) -> None:
        """Qayta tekshirish yangi urinish EMAS."""
        ac(user, problem, language)
        oldin = Problem.objects.get(pk=problem.pk).attempt_count

        call_command("rejudge", problem=problem.slug)

        assert Problem.objects.get(pk=problem.pk).attempt_count == oldin

    def test_verdict_boyicha_filtr(self, user, problem, language, memory_judge) -> None:
        ac(user, problem, language)
        Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="y", verdict=Verdict.WA
        )

        call_command("rejudge", problem=problem.slug, verdict="wa")

        assert len(memory_judge.jobs) == 1

    def test_limit_partiyani_cheklaydi(self, user, problem, language, memory_judge) -> None:
        for _ in range(3):
            ac(user, problem, language)

        call_command("rejudge", problem=problem.slug, limit=2)

        assert len(memory_judge.jobs) == 2


@pytest.mark.django_db
class TestOlikVerdiktlar:
    """E'lon qilingan, lekin hech qanday kod yozmaydigan verdiktlar ulandi."""

    def test_rejudge_testing_aborted_qoyadi(self, user, problem, language, memory_judge) -> None:
        """`PENDING` foydalanuvchi uchun yangi yuborishdan farq qilmasdi."""
        a = ac(user, problem, language)

        call_command("rejudge", problem=problem.slug)

        a.refresh_from_db()
        assert a.verdict == Verdict.TESTING_ABORTED

    def test_qayta_tekshirilayotganni_ikkinchi_marta_olmaydi(
        self, user, problem, language, memory_judge
    ) -> None:
        ac(user, problem, language)
        call_command("rejudge", problem=problem.slug)
        memory_judge.jobs.clear()

        call_command("rejudge", problem=problem.slug)

        assert memory_judge.jobs == [], "allaqachon navbatda"

    def test_yoqolgan_ish_denial_of_judgement(self, user, problem, language, memory_judge) -> None:
        """`IE` masala xatosini ham bildirardi — operator ajrata olmasdi."""
        from datetime import timedelta

        from django.utils import timezone

        from judging.tasks import reap_stuck

        a = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="x",
            verdict=Verdict.PENDING,
        )
        eski = timezone.now() - timedelta(hours=2)
        Attempt.objects.filter(pk=a.pk).update(created_at=eski, requeued_at=eski)

        reap_stuck()

        a.refresh_from_db()
        assert a.verdict == Verdict.DENIAL_OF_JUDGEMENT

    def test_skip_ac_ni_va_yechimni_bekor_qiladi(self, user, problem, language) -> None:
        a = ac(user, problem, language)
        assert UserSolvedProblem.objects.filter(user=user, problem=problem).exists()

        call_command("skip_attempts", user=user.username, problem=problem.slug)

        a.refresh_from_db()
        assert a.verdict == Verdict.SKIPPED
        assert not UserSolvedProblem.objects.filter(user=user, problem=problem).exists()
        assert Problem.objects.get(pk=problem.pk).solved_count == 0

    def test_skip_filtrsiz_ishlamaydi(self, user, problem, language) -> None:
        ac(user, problem, language)

        with pytest.raises(CommandError):
            call_command("skip_attempts", user=user.username)
