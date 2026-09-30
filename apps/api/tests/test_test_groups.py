"""Test guruhlari — siyosat, API, judge va nashr darvozasi (PROMPT_0 §3 · ADR 0051).

Uchta haqiqiy oqim sinaladi, chunki guruh faqat metadata emas:

1. siyosat funksiyalari (ko'rinish, nashr talabi, judge istisnosi)
2. yuklash API'si — standart guruh, `is_sample` mosligi, hajm chegarasi
3. judge payload'i — `STRESS` baholashga KIRMASLIGI

`ProblemCodeSequence` poygasidan qochish uchun masalalar `code` ni ochiq
beradi (o'lchandi: umumiy fixture'lar `max(code)+1` yozadi va sequence bilan
to'qnashadi).
"""

from __future__ import annotations

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from judging.services import build_standalone_job
from problems import testgroups
from problems.models import Language, Problem, TestCase
from problems.storage import MAX_TEST_BYTES


def _problem(slug: str, code: int) -> Problem:
    return Problem.objects.create(
        slug=slug, title=slug, statement="…", difficulty=800, is_public=False, code=code
    )


def _test(problem: Problem, order: int, group: str, **kw) -> TestCase:
    return TestCase.objects.create(
        problem=problem,
        order=order,
        input_ref=f"s3://x/{order}.in",
        output_ref=f"s3://x/{order}.out",
        group=group,
        **kw,
    )


# ── 1. Siyosat ────────────────────────────────────────────────────────


class TestGroupPolicy:
    def test_sample_is_the_only_public_group(self) -> None:
        assert testgroups.is_public_group(TestCase.Group.SAMPLE)
        for group in (
            TestCase.Group.MINIMAL,
            TestCase.Group.BOUNDARY,
            TestCase.Group.SPECIAL,
            TestCase.Group.RANDOM,
            TestCase.Group.ADVERSARIAL,
            TestCase.Group.MAXIMUM,
            TestCase.Group.STRESS,
        ):
            assert not testgroups.is_public_group(group)

    def test_missing_required_groups_reports_both(self) -> None:
        assert testgroups.missing_required_groups([]) == [
            TestCase.Group.BOUNDARY,
            TestCase.Group.MAXIMUM,
        ]

    def test_unclassified_does_not_satisfy_a_requirement(self) -> None:
        """Ko'chirish holati darvozani jimgina ochmasligi shart."""
        assert testgroups.missing_required_groups([TestCase.Group.UNCLASSIFIED]) == [
            TestCase.Group.BOUNDARY,
            TestCase.Group.MAXIMUM,
        ]

    def test_present_groups_are_removed_from_the_report(self) -> None:
        assert (
            testgroups.missing_required_groups(
                [TestCase.Group.BOUNDARY, TestCase.Group.MAXIMUM, TestCase.Group.RANDOM]
            )
            == []
        )

    def test_stress_is_not_judged(self) -> None:
        assert not testgroups.is_judged(TestCase.Group.STRESS)
        assert testgroups.is_judged(TestCase.Group.BOUNDARY)
        assert testgroups.is_judged(TestCase.Group.SAMPLE)


# ── 2. Yuklash API ────────────────────────────────────────────────────


@pytest.fixture
def staff_client(db):
    user = User.objects.create_user("tg-staff", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _upload(client: APIClient, problem: Problem, **body):
    payload = {"order": 1, "input": "1\n", "expected": "2\n", **body}
    return client.post(reverse("staff-problem-tests", args=[problem.slug]), payload, format="json")


@pytest.mark.django_db
class TestUploadGroup:
    @pytest.fixture(autouse=True)
    def _storage(self, fake_hack_storage: dict[str, str]) -> dict[str, str]:
        """S3 o'rniga xotira — yuklash sinovlari MinIO'siz ishlaydi.

        Busiz `storage.put_test_data` haqiqiy S3 ga murojaat qiladi va
        `Invalid endpoint` beradi (o'lchandi), ya'ni test muhitga bog'lanib
        qolardi.
        """
        return fake_hack_storage

    def test_default_group_is_unclassified(self, staff_client) -> None:
        problem = _problem("tg-default", 7001)
        response = _upload(staff_client, problem)
        assert response.status_code == 201, response.json()
        assert problem.tests.get().group == TestCase.Group.UNCLASSIFIED

    def test_explicit_group_is_kept(self, staff_client) -> None:
        problem = _problem("tg-explicit", 7002)
        response = _upload(staff_client, problem, group=TestCase.Group.BOUNDARY)
        assert response.status_code == 201, response.json()
        assert problem.tests.get().group == TestCase.Group.BOUNDARY

    def test_sample_flag_forces_the_sample_group(self, staff_client) -> None:
        problem = _problem("tg-sample", 7003)
        response = _upload(staff_client, problem, is_sample=True)
        assert response.status_code == 201, response.json()
        row = problem.tests.get()
        assert row.is_sample is True
        assert row.group == TestCase.Group.SAMPLE

    def test_sample_group_without_the_flag_is_refused(self, staff_client) -> None:
        problem = _problem("tg-mismatch", 7004)
        response = _upload(staff_client, problem, group=TestCase.Group.SAMPLE)
        assert response.status_code == 400, response.json()
        assert not problem.tests.exists()

    def test_sample_flag_with_a_foreign_group_is_refused(self, staff_client) -> None:
        problem = _problem("tg-conflict", 7005)
        response = _upload(staff_client, problem, is_sample=True, group=TestCase.Group.RANDOM)
        assert response.status_code == 400, response.json()

    def test_oversized_input_is_refused(self, staff_client) -> None:
        """§8.4 — chegara yo'q edi; `CharField` cheksiz edi (o'lchandi)."""
        problem = _problem("tg-big", 7006)
        response = _upload(staff_client, problem, input="x" * (MAX_TEST_BYTES + 1))
        assert response.status_code == 400, response.json()
        assert not problem.tests.exists()

    def test_a_large_but_legal_test_is_accepted(self, staff_client) -> None:
        problem = _problem("tg-ok", 7007)
        response = _upload(staff_client, problem, input="x" * (MAX_TEST_BYTES - 1))
        assert response.status_code == 201, response.json()


# ── 3. Judge payload ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestJudgeSelection:
    def test_stress_tests_do_not_enter_the_job(self) -> None:
        problem = _problem("tg-judge", 7008)
        _test(problem, 1, TestCase.Group.SAMPLE, is_sample=True)
        _test(problem, 2, TestCase.Group.BOUNDARY)
        _test(problem, 3, TestCase.Group.STRESS)

        language = Language.objects.create(
            code="py-probe",
            name="Python probe",
            version="3.12",
            source_file="main.py",
            compile_cmd=["true"],
            run_cmd=["python", "main.py"],
        )
        job = build_standalone_job(problem, "print(1)", language)
        assert [t["index"] for t in job.tests] == [1, 2]

    def test_an_empty_test_set_still_builds(self) -> None:
        problem = _problem("tg-empty", 7009)
        language = Language.objects.create(
            code="py-probe2",
            name="Python probe 2",
            version="3.12",
            source_file="main.py",
            compile_cmd=["true"],
            run_cmd=["python", "main.py"],
        )
        job = build_standalone_job(problem, "print(1)", language)
        assert job.tests == []


# ── 4. Nashr darvozasi ────────────────────────────────────────────────


@pytest.mark.django_db
class TestPublishGroupGate:
    def _publish(self, client: APIClient, problem: Problem):
        return client.patch(
            reverse("staff-problem-detail", args=[problem.slug]),
            {"is_public": True},
            format="json",
        )

    @override_settings(READINESS_ENFORCE=True)
    def test_missing_group_blocks_publication(self, staff_client) -> None:
        problem = _problem("tg-gate", 7010)
        _test(problem, 1, TestCase.Group.RANDOM)
        response = self._publish(staff_client, problem)
        assert response.status_code == 400, response.json()
        assert "TEST_GROUP_MISSING" in str(response.json())
        problem.refresh_from_db()
        assert problem.is_public is False

    @override_settings(READINESS_ENFORCE=True)
    def test_required_groups_open_the_gate(self, staff_client) -> None:
        problem = _problem("tg-gate-ok", 7011)
        _test(problem, 1, TestCase.Group.BOUNDARY)
        _test(problem, 2, TestCase.Group.MAXIMUM)
        response = self._publish(staff_client, problem)
        assert response.status_code == 200, response.json()
        problem.refresh_from_db()
        assert problem.is_public is True

    @override_settings(READINESS_ENFORCE=False)
    def test_staged_rollout_keeps_legacy_publishable(self, staff_client) -> None:
        """Bayroq o'chiq bo'lsa eski kontent bloklanmaydi (ADR 0050)."""
        problem = _problem("tg-gate-legacy", 7012)
        _test(problem, 1, TestCase.Group.UNCLASSIFIED)
        response = self._publish(staff_client, problem)
        assert response.status_code == 200, response.json()
        problem.refresh_from_db()
        assert problem.is_public is True
