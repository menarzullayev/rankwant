"""Nashr darvozalari, revision va integrity (PROMPT_0 §6 · §9 · §10 · ADR 0052).

Sinovlar «maydon bor» ni emas, ISHLASHNI isbotlaydi:
  - to'liqsiz shart nashrga o'tkazilmasligi
  - yetishmayotgan guruh nashrni to'sishi
  - har gate uchun BARQAROR kod qaytishi
  - muzlatilgan revision o'zgarmasligi
  - paket xeshi artefakt mutatsiyasini aniqlashi

`ProblemCodeSequence` poygasidan qochish uchun masalalar `code` ni ochiq
beradi (o'lchandi: umumiy fixture'lar `max(code)+1` yozadi va to'qnashadi).
"""

from __future__ import annotations

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import User
from problems import release
from problems.models import (
    Language,
    LimitCalibration,
    Problem,
    ProblemRevision,
    ProblemSolution,
    RevisionStatus,
    SolutionRole,
    TestCase,
    Validator,
)


def _problem(slug: str, code: int, **kw) -> Problem:
    return Problem.objects.create(
        slug=slug,
        title=slug,
        statement="…",
        input_format="n",
        output_format="javob",
        difficulty=800,
        code=code,
        **kw,
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


def _full(problem: Problem) -> None:
    """Barcha gate'lar o'tishi uchun kerakli minimal to'plam."""
    _test(problem, 1, TestCase.Group.SAMPLE, is_sample=True)
    _test(problem, 2, TestCase.Group.BOUNDARY)
    _test(problem, 3, TestCase.Group.MAXIMUM)
    problem.readiness = Problem.Readiness.VALIDATED
    problem.checker_verified_at = timezone.now()
    problem.save(update_fields=["readiness", "checker_verified_at", "updated_at"])
    Validator.objects.create(
        problem=problem,
        language=_language("py-val"),
        source="print(1)",
        verified_at=timezone.now(),
    )
    ProblemSolution.objects.create(
        problem=problem,
        role=SolutionRole.REFERENCE,
        language=_language("py-ref"),
        source="print(1)",
    )


def _language(code: str) -> Language:
    language, _ = Language.objects.get_or_create(
        code=code,
        defaults={
            "name": code,
            "version": "3.12",
            "source_file": "main.py",
            "compile_cmd": ["true"],
            "run_cmd": ["python", "main.py"],
        },
    )
    return language


@pytest.fixture
def staff_client(db):
    user = User.objects.create_user("rel-staff", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ── §6 Statement to'liqligi ───────────────────────────────────────────


@pytest.mark.django_db
class TestStatementGate:
    def test_whitespace_only_counts_as_missing(self) -> None:
        problem = _problem("st-blank", 7101)
        problem.statement = "   \n\t "
        assert release.missing_statement_fields(problem) == ["statement"]

    def test_missing_fields_block_the_gate(self) -> None:
        problem = _problem("st-part", 7102)
        problem.input_format = ""
        gate = release.statement_gate(problem)
        assert gate.passed is False
        assert gate.detail == "missing: input_format"

    def test_no_sample_blocks_the_gate(self) -> None:
        problem = _problem("st-nosample", 7103)
        gate = release.statement_gate(problem)
        assert gate.passed is False
        assert "sample" in gate.detail

    def test_complete_statement_passes(self) -> None:
        problem = _problem("st-ok", 7104)
        _test(problem, 1, TestCase.Group.SAMPLE, is_sample=True)
        assert release.statement_gate(problem).passed is True


# ── §9 Release checklist ──────────────────────────────────────────────


@pytest.mark.django_db
class TestReleaseChecklist:
    def test_all_gates_are_reported(self) -> None:
        problem = _problem("rel-all", 7105)
        report = release.release_report(problem)
        assert len(report) == 8
        assert {g.code for g in report} == {
            release.STATEMENT_INCOMPLETE,
            release.TEST_GROUP_MISSING,
            release.VALIDATOR_NOT_VERIFIED,
            release.REFERENCE_FAILED,
            release.CHECKER_NOT_VERIFIED,
            release.LIMITS_NOT_CALIBRATED,
            release.REVIEW_REQUIRED,
            release.REVISION_NOT_FROZEN,
        }

    def test_codes_are_stable_and_sorted_by_gate_order(self) -> None:
        problem = _problem("rel-codes", 7106)
        codes = release.blocking_codes(problem)
        assert codes[0] == release.STATEMENT_INCOMPLETE
        assert release.REVISION_NOT_FROZEN in codes

    def test_a_complete_package_passes_every_gate(self) -> None:
        problem = _problem("rel-full", 7107)
        _full(problem)
        revision = release.create_revision(problem)
        release.freeze_revision(revision)
        problem.current_revision = revision
        problem.save(update_fields=["current_revision", "updated_at"])
        LimitCalibration.objects.create(
            revision=revision,
            measurements={"wall_ms": 120, "peak_kb": 2048, "tests": 3},
            time_limit_ms=1000,
            memory_limit_kb=262144,
        )
        assert release.blocking_codes(problem) == []
        assert release.release_payload(problem)["can_publish"] is True

    def test_payload_names_the_failed_gates(self) -> None:
        problem = _problem("rel-fail", 7108)
        payload = release.release_payload(problem)
        assert payload["can_publish"] is False
        assert {row["code"] for row in payload["failed"]} == set(
            release.blocking_codes(problem)
        )


# ── §10 Revision va immutability ──────────────────────────────────────


@pytest.mark.django_db
class TestRevision:
    def test_editing_creates_a_new_revision(self) -> None:
        problem = _problem("rev-new", 7109)
        first = release.create_revision(problem)
        second = release.create_revision(problem)
        assert first.version != second.version
        assert second.version == first.version + 1

    def test_freeze_writes_the_package_hash(self) -> None:
        problem = _problem("rev-hash", 7110)
        _test(problem, 1, TestCase.Group.SAMPLE, is_sample=True)
        revision = release.create_revision(problem)
        assert revision.package_hash == ""
        release.freeze_revision(revision)
        assert revision.package_hash
        assert revision.status == RevisionStatus.FROZEN
        assert revision.is_frozen is True

    def test_hash_detects_a_mutated_artifact(self) -> None:
        """§8 — artefakt o'zgarsa integrity mismatch aniqlanadi."""
        problem = _problem("rev-mutate", 7111)
        _test(problem, 1, TestCase.Group.SAMPLE, is_sample=True)
        revision = release.create_revision(problem)
        release.freeze_revision(revision)
        assert release.verify_package(revision) is True

        revision.package["statement"]["statement"] = "boshqa matn"
        assert release.verify_package(revision) is False

    def test_hash_is_stable_across_key_order(self) -> None:
        """Lug'at tartibi o'zgarsa xesh o'zgarmasligi kerak."""
        package = {"a": 1, "b": {"c": 2, "d": 3}}
        swapped = {"b": {"d": 3, "c": 2}, "a": 1}
        assert release.package_hash(package) == release.package_hash(swapped)

    def test_snapshot_records_tests_and_limits(self) -> None:
        problem = _problem("rev-snap", 7112)
        _test(problem, 1, TestCase.Group.BOUNDARY)
        package = release.snapshot_package(problem)
        assert len(package["tests"]) == 1
        assert package["tests"][0]["group"] == TestCase.Group.BOUNDARY
        assert package["limits"]["time_limit_ms"] == problem.time_limit_ms

    def test_publish_blocks_until_the_gates_pass(self) -> None:
        from rest_framework.exceptions import ValidationError

        problem = _problem("rev-block", 7113)
        revision = release.create_revision(problem)
        release.freeze_revision(revision)
        with pytest.raises(ValidationError):
            release.assert_publishable(problem)

    def test_publish_sets_the_pointer_and_deprecates_the_old_one(self) -> None:
        problem = _problem("rev-pub", 7114)
        _full(problem)
        revision = release.create_revision(problem)
        release.freeze_revision(revision)
        problem.current_revision = revision
        problem.save(update_fields=["current_revision", "updated_at"])
        LimitCalibration.objects.create(
            revision=revision,
            time_limit_ms=1000,
            memory_limit_kb=262144,
            measurements={"wall_ms": 90, "peak_kb": 1024, "tests": 3},
        )
        release.assert_publishable(problem)
        release.publish_revision(revision)

        problem.refresh_from_db()
        assert problem.current_revision_id == revision.pk
        revision.refresh_from_db()
        assert revision.status == RevisionStatus.PUBLISHED
        assert revision.published_at is not None

    def test_uniqueness_of_version_is_enforced(self) -> None:
        from django.db import IntegrityError, transaction

        problem = _problem("rev-uniq", 7115)
        release.create_revision(problem)
        with pytest.raises(IntegrityError), transaction.atomic():
            ProblemRevision.objects.create(problem=problem, version=1)


# ── API ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestReleaseApi:
    def test_checklist_endpoint_answers_why(self, staff_client) -> None:
        problem = _problem("api-why", 7116)
        response = staff_client.get(
            f"/api/v1/staff/problems/{problem.slug}/release-checklist/"
        )
        assert response.status_code == 200, response.json()
        body = response.json()
        assert body["can_publish"] is False
        assert body["failed"]

    def test_revision_endpoint_creates_and_freezes(self, staff_client) -> None:
        problem = _problem("api-rev", 7117)
        created = staff_client.post(
            f"/api/v1/staff/problems/{problem.slug}/revisions/"
        )
        assert created.status_code == 201, created.json()
        revision_id = created.json()["id"]

        frozen = staff_client.post(
            f"/api/v1/staff/problems/{problem.slug}/revisions/{revision_id}/freeze/"
        )
        assert frozen.status_code == 200, frozen.json()
        assert frozen.json()["status"] == RevisionStatus.FROZEN
        assert frozen.json()["integrity_ok"] is True

    def test_publish_endpoint_refuses_an_incomplete_package(self, staff_client) -> None:
        problem = _problem("api-pub-fail", 7118)
        created = staff_client.post(
            f"/api/v1/staff/problems/{problem.slug}/revisions/"
        )
        revision_id = created.json()["id"]
        response = staff_client.post(
            f"/api/v1/staff/problems/{problem.slug}/revisions/{revision_id}/publish/"
        )
        assert response.status_code == 400, response.json()
        assert "code" in str(response.json())
