"""Submit → verdict → reyting zanjiri. DoD: qamrov MAJBURIY."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from judging.models import Attempt, AttemptTestResult
from judging.services import apply_result, build_job
from judging.verdicts import Verdict
from ratings.models import RatingHistory, UserSolvedProblem


@pytest.fixture
def client(user) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.mark.django_db
class TestSubmit:
    def test_submit_navbatga_tushadi(
        self, client: APIClient, problem, language, memory_judge
    ) -> None:
        r = client.post(
            reverse("attempt-list"),
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": "int main(){}",
            },
        )
        assert r.status_code == 201
        assert r.json()["verdict"] == Verdict.PENDING
        assert len(memory_judge.jobs) == 1

    def test_attempt_avval_saqlanadi(self, client: APIClient, problem, language) -> None:
        """Navbat yiqilsa ham submission yo'qolmasligi kerak."""
        client.post(
            reverse("attempt-list"),
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": "x",
            },
        )
        assert Attempt.objects.count() == 1

    def test_katta_manba_rad_etiladi(self, client: APIClient, problem, language) -> None:
        r = client.post(
            reverse("attempt-list"),
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": "x" * (64 * 1024 + 1),
            },
        )
        assert r.status_code == 400

    def test_bosh_manba_rad_etiladi(self, client: APIClient, problem, language) -> None:
        r = client.post(
            reverse("attempt-list"),
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": "   ",
            },
        )
        assert r.status_code == 400

    def test_anonim_submit_qila_olmaydi(self, problem, language) -> None:
        r = APIClient().post(
            reverse("attempt-list"),
            {
                "problem": problem.slug,
                "language": language.code,
                "source_code": "x",
            },
        )
        assert r.status_code in (401, 403)

    def test_job_limitlarni_masaladan_oladi(self, user, problem, language) -> None:
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        job = build_job(attempt)
        assert job.limits["time_ms"] == problem.time_limit_ms
        assert job.limits["memory_kb"] == problem.memory_limit_kb
        assert job.language["code"] == language.code


@pytest.mark.django_db
class TestApplyResult:
    def _attempt(self, user, problem, language) -> Attempt:
        return Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )

    def test_ac_reytingni_oshiradi(self, user, problem, language) -> None:
        attempt = self._attempt(user, problem, language)
        apply_result(
            {
                "attempt_id": attempt.pk,
                "verdict": "AC",
                "score": 100,
                "time_ms": 12,
                "memory_kb": 3000,
                "per_test": [{"index": 1, "verdict": "AC", "time_ms": 12, "memory_kb": 3000}],
            }
        )
        attempt.refresh_from_db()
        user.refresh_from_db()
        assert attempt.verdict == Verdict.AC
        assert attempt.judged_at is not None
        assert UserSolvedProblem.objects.filter(user=user, problem=problem).exists()
        assert user.rating_skills == 800
        assert AttemptTestResult.objects.filter(attempt=attempt).count() == 1

    def test_wa_reytingga_tegmaydi(self, user, problem, language) -> None:
        attempt = self._attempt(user, problem, language)
        apply_result({"attempt_id": attempt.pk, "verdict": "WA", "failed_test_index": 2})
        user.refresh_from_db()
        assert user.rating_skills == 0
        assert not UserSolvedProblem.objects.exists()

    def test_ikkinchi_ac_qayta_hisoblamaydi(self, user, problem, language) -> None:
        """Faqat BIRINCHI AC hisoblanadi."""
        for _ in range(2):
            attempt = self._attempt(user, problem, language)
            apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        user.refresh_from_db()
        assert UserSolvedProblem.objects.count() == 1
        assert user.rating_skills == 800

    def test_rating_history_sabab_bilan(self, user, problem, language) -> None:
        """Principle #2: har o'zgarishning sababi yoziladi."""
        attempt = self._attempt(user, problem, language)
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        entry = RatingHistory.objects.get(user=user, rating_type="skills")
        assert entry.delta == 800
        assert entry.reason == RatingHistory.Reason.PROBLEM_SOLVED
        assert entry.ref_id == problem.slug

    def test_notanish_attempt_yiqilmaydi(self) -> None:
        assert apply_result({"attempt_id": 999999, "verdict": "AC"}) is None

    def test_security_violation_yoziladi(self, user, problem, language) -> None:
        attempt = self._attempt(user, problem, language)
        apply_result({"attempt_id": attempt.pk, "verdict": "SECURITY_VIOLATION"})
        attempt.refresh_from_db()
        assert attempt.verdict == Verdict.SECURITY_VIOLATION


@pytest.mark.django_db
class TestReratingAffectsSkills:
    def test_qiyinlik_ozgarsa_qayta_hisoblanadi(self, user, problem, language) -> None:
        """ADR-0007: Skills JORIY qiyinlikdan hisoblanadi."""
        from ratings.services import recalc_skills_for_problem

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        user.refresh_from_db()
        assert user.rating_skills == 800

        problem.difficulty = 1500
        problem.save()
        assert recalc_skills_for_problem(problem.pk) == 1

        user.refresh_from_db()
        assert user.rating_skills == 1500
        assert RatingHistory.objects.filter(
            user=user, reason=RatingHistory.Reason.PROBLEM_RERATED
        ).exists()


@pytest.mark.django_db
class TestSourceVisibility:
    def test_boshqa_foydalanuvchi_manbani_kormaydi(
        self, user, other_user, problem, language
    ) -> None:
        """IDOR himoyasi — test-strategy § security."""
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="MAXFIY"
        )
        c = APIClient()
        c.force_authenticate(user=other_user)
        data = c.get(reverse("attempt-detail", args=[attempt.pk])).json()
        assert "source_code" not in data

    def test_egasi_koradi(self, user, problem, language) -> None:
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="MENIKI"
        )
        c = APIClient()
        c.force_authenticate(user=user)
        assert c.get(reverse("attempt-detail", args=[attempt.pk])).json()["source_code"] == "MENIKI"


@pytest.mark.django_db
class TestCustomRun:
    """PRD P0-4 — custom test."""

    def _client(self, user):
        c = APIClient()
        c.force_authenticate(user=user)
        return c

    def test_custom_run_navbatga_tushadi(self, user, language, memory_judge) -> None:
        from django.urls import reverse as rev

        r = self._client(user).post(
            rev("customrun-list"),
            {
                "language": language.code,
                "source_code": "print(input())",
                "stdin": "salom",
            },
        )
        assert r.status_code == 201
        assert r.json()["verdict"] == Verdict.PENDING
        job = memory_judge.jobs[-1]
        assert job.mode == "custom"
        assert job.custom_run_id is not None
        assert job.tests[0]["input"] == "salom"

    def test_natija_yoziladi(self, user, language) -> None:
        from judging.models import CustomRun
        from judging.services import apply_custom_result

        run = CustomRun.objects.create(user=user, language=language, source_code="x", stdin="1 2")
        apply_custom_result(
            {
                "custom_run_id": run.pk,
                "verdict": "AC",
                "time_ms": 8,
                "memory_kb": 2000,
                "per_test": [{"index": 1, "verdict": "AC", "stdout": "3\n"}],
            }
        )
        run.refresh_from_db()
        assert run.verdict == Verdict.AC
        assert run.stdout == "3\n"
        assert run.judged_at is not None

    def test_boshqa_foydalanuvchi_kormaydi(self, user, other_user, language) -> None:
        from django.urls import reverse as rev

        from judging.models import CustomRun

        run = CustomRun.objects.create(user=user, language=language, source_code="MAXFIY")
        r = self._client(other_user).get(rev("customrun-detail", args=[run.pk]))
        assert r.status_code == 404

    def test_reytingga_tegmaydi(self, user, language) -> None:
        """Custom test urinishlar tarixiga ham, reytingga ham ta'sir qilmaydi."""
        from judging.models import Attempt, CustomRun
        from judging.services import apply_custom_result

        run = CustomRun.objects.create(user=user, language=language, source_code="x")
        apply_custom_result({"custom_run_id": run.pk, "verdict": "AC"})
        user.refresh_from_db()
        assert user.rating_skills == 0
        assert Attempt.objects.count() == 0
        assert not UserSolvedProblem.objects.exists()

    def test_bosh_manba_rad_etiladi(self, user, language) -> None:
        from django.urls import reverse as rev

        r = self._client(user).post(
            rev("customrun-list"),
            {
                "language": language.code,
                "source_code": "  ",
                "stdin": "",
            },
        )
        assert r.status_code == 400


@pytest.mark.django_db
class TestRecommendation:
    """PRD P1-2 — masala tavsiyasi."""

    def test_yangi_foydalanuvchiga_eng_oson(self, user, problem, hard_problem) -> None:
        from problems.recommend import recommend, target_difficulty

        assert target_difficulty(user) == 800
        assert problem in list(recommend(user))

    def test_yechilganlar_chiqarib_tashlanadi(self, user, problem, language) -> None:
        from problems.recommend import recommend

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        assert problem not in list(recommend(user))

    def test_daraja_oshadi(self, user, problem, hard_problem, language) -> None:
        from problems.recommend import target_difficulty

        attempt = Attempt.objects.create(
            user=user, problem=hard_problem, language=language, source_code="x"
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC"})
        # 2500 yechildi → keyingi qadam 2600
        assert target_difficulty(user) == 2600

    def test_api(self, user, problem) -> None:
        from django.urls import reverse as rev

        c = APIClient()
        c.force_authenticate(user=user)
        body = c.get(rev("recommendation")).json()
        assert body["target_difficulty"] == 800
        assert any(p["slug"] == problem.slug for p in body["results"])

    def test_anonim_kira_olmaydi(self) -> None:
        from django.urls import reverse as rev

        assert APIClient().get(rev("recommendation")).status_code in (401, 403)


class TestSubtaskScoring:
    """IOI ballash — subtask bo'lsa judge `ioi` rejimida chaqiriladi."""

    def test_subtasksiz_masala_acm_rejimida(self, problem, language, user) -> None:
        from judging.models import Attempt
        from judging.services import build_job

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        job = build_job(attempt)

        assert job.mode == "acm"
        assert job.subtasks == []

    def test_subtask_bolsa_ioi_rejimi_va_guruhlar(self, problem, language, user) -> None:
        from judging.models import Attempt
        from judging.services import build_job
        from problems.models import Subtask
        from problems.models import TestCase as PTest

        # Fixture bergan testni olib tashlaymiz — bu test masalaning
        # testlari AYNAN quyidagi ikkitasi ekaniga tayanadi.
        problem.tests.all().delete()
        first = Subtask.objects.create(problem=problem, order=1, points=40, scoring="min")
        second = Subtask.objects.create(problem=problem, order=2, points=60, scoring="min")
        PTest.objects.create(
            problem=problem,
            order=1,
            input_ref="s3://x/1.in",
            output_ref="s3://x/1.out",
            subtask=first,
        )
        PTest.objects.create(
            problem=problem,
            order=2,
            input_ref="s3://x/2.in",
            output_ref="s3://x/2.out",
            subtask=second,
        )

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        job = build_job(attempt)

        assert job.mode == "ioi"
        assert [s["points"] for s in job.subtasks] == [40, 60]
        assert [t["subtask"] for t in job.tests] == [first.pk, second.pk]


class TestLanguageLimits:
    """Til ustma-ust limiti — Python C++ dan sekinroq."""

    def test_ustma_ust_limit_qollanadi(self, problem, language, user) -> None:
        from judging.models import Attempt
        from judging.services import build_job
        from problems.models import ProblemLanguage

        ProblemLanguage.objects.create(problem=problem, language=language, time_limit_ms=3000)
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )

        job = build_job(attempt)
        assert job.limits["time_ms"] == 3000
        # Xotira ustma-ust yozilmagan — masala limiti qoladi.
        assert job.limits["memory_kb"] == problem.memory_limit_kb

    def test_ustma_ust_yoq_bolsa_masala_limiti(self, problem, language, user) -> None:
        from judging.models import Attempt
        from judging.services import build_job

        attempt = Attempt.objects.create(
            user=user, problem=problem, language=language, source_code="x"
        )
        assert build_job(attempt).limits["time_ms"] == problem.time_limit_ms


def test_masala_cheklagan_tilda_yechim_qabul_qilinmaydi(problem, user, language, db) -> None:
    """Django/SQL masalasi C++ da ma'noga ega emas — KEP ham cheklaydi."""
    from problems.models import Language, ProblemLanguage

    python = Language.objects.create(
        code="py313", name="Python", version="3.13", run_cmd=["python3", "{src}"]
    )
    ProblemLanguage.objects.create(problem=problem, language=python)

    client = APIClient()
    client.force_authenticate(user)
    payload = {"problem": problem.slug, "language": "cpp23", "source_code": "int main(){}"}

    response = client.post(reverse("attempt-list"), payload)

    assert response.status_code == 400
    assert "py313" in str(response.data["error"]["details"]["language"])


def test_testsiz_masalaga_yuborib_bolmaydi(hard_problem, user, language) -> None:
    """Judge testsiz job uchun IE qaytaradi — bunga yo'l qo'ymaymiz."""
    client = APIClient()
    client.force_authenticate(user)
    payload = {
        "problem": hard_problem.slug,
        "language": language.code,
        "source_code": "int main(){}",
    }

    response = client.post(reverse("attempt-list"), payload)

    assert response.status_code == 400
    assert "test" in str(response.data["error"]["details"]["problem"]).lower()
