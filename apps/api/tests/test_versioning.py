"""Versioning points (decision 2026-10-27): judge protocol, attempt revision."""

from __future__ import annotations

import json
from io import StringIO

import pytest
from django.core.management import call_command

from judging.models import Attempt
from judging.provider import JUDGE_PROTOCOL_VERSION, JudgeJob, result_is_understood
from judging.tasks import drain_results
from problems import release
from problems.models import Problem


def _attempt(problem, user, language) -> Attempt:
    return Attempt.objects.create(
        user=user, problem=problem, language=language, source_code="x", verdict="PENDING"
    )


def _job() -> JudgeJob:
    return JudgeJob(
        job_id="j",
        attempt_id=1,
        language={},
        source="",
        limits={},
        tests=[],
        checker={},
    )


class TestProtocolVersion:
    def test_every_job_carries_the_version(self) -> None:
        assert json.loads(_job().to_json())["protocol_version"] == JUDGE_PROTOCOL_VERSION

    def test_understood_results(self) -> None:
        assert result_is_understood({})  # a judge from before the field
        assert result_is_understood({"protocol_version": JUDGE_PROTOCOL_VERSION})
        assert not result_is_understood({"protocol_version": JUDGE_PROTOCOL_VERSION + 1})

    @pytest.mark.django_db
    def test_newer_result_is_parked_not_applied(self, problem, user, language, memory_judge):
        attempt = _attempt(problem, user, language)
        memory_judge.results.append(
            {
                "protocol_version": JUDGE_PROTOCOL_VERSION + 1,
                "job_id": "j",
                "attempt_id": attempt.pk,
                "verdict": "AC",
                "score": 100,
                "per_test": [],
            }
        )
        assert drain_results() == 0
        attempt.refresh_from_db()
        assert attempt.verdict == "PENDING"
        assert len(memory_judge.parked) == 1
        assert memory_judge.results == []


def _published(problem: Problem):
    revision = release.create_revision(problem)
    release.freeze_revision(revision)
    problem.current_revision = revision
    problem.save(update_fields=["current_revision", "updated_at"])
    return revision


@pytest.mark.django_db
class TestAttemptRevision:
    def test_new_attempt_is_stamped_with_current_revision(self, problem, user, language) -> None:
        revision = _published(problem)
        assert _attempt(problem, user, language).problem_revision_id == revision.pk

    def test_unpublished_problem_leaves_it_null(self, problem, user, language) -> None:
        assert _attempt(problem, user, language).problem_revision_id is None

    def test_explicit_revision_is_kept(self, problem, user, language) -> None:
        first = _published(problem)
        second = release.create_revision(problem)
        attempt = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="x",
            problem_revision=second,
        )
        assert attempt.problem_revision_id == second.pk != first.pk

    def test_rejudge_keeps_the_revision_unless_asked(
        self, problem, user, language, memory_judge
    ) -> None:
        old = _published(problem)
        attempt = _attempt(problem, user, language)
        Attempt.objects.filter(pk=attempt.pk).update(verdict="WA")
        new = release.create_revision(problem)
        release.freeze_revision(new)
        problem.current_revision = new
        problem.save(update_fields=["current_revision", "updated_at"])

        call_command("rejudge", problem=problem.slug, stdout=StringIO())
        attempt.refresh_from_db()
        assert attempt.problem_revision_id == old.pk

        Attempt.objects.filter(pk=attempt.pk).update(verdict="WA")
        call_command(
            "rejudge", problem=problem.slug, adopt_current_revision=True, stdout=StringIO()
        )
        attempt.refresh_from_db()
        assert attempt.problem_revision_id == new.pk


@pytest.mark.django_db
class TestFormulaVersion:
    def test_new_history_rows_carry_the_current_version(self, user) -> None:
        from ratings import formulas
        from ratings.models import RatingHistory

        row = RatingHistory.objects.create(
            user=user,
            rating_type="skills",
            value_before=0,
            value_after=10,
            delta=10,
            reason="problem_solved",
        )
        row.refresh_from_db()
        assert row.formula_version == formulas.FORMULA_VERSION

    def test_the_stored_version_can_stay_unknown(self, user) -> None:
        from ratings.models import RatingHistory

        row = RatingHistory.objects.create(
            user=user,
            rating_type="skills",
            value_before=0,
            value_after=10,
            delta=10,
            reason="problem_solved",
            formula_version=None,
        )
        row.refresh_from_db()
        assert row.formula_version is None


class TestCacheVersion:
    def test_the_version_is_folded_into_every_key(self) -> None:
        from django.conf import settings
        from django.core.cache import cache

        assert settings.CACHES["default"]["VERSION"] == settings.CACHE_VERSION
        cache.set("versioning:probe", "x")
        try:
            assert cache.get("versioning:probe") == "x"
            # What a bumped CACHE_VERSION would read: nothing.
            assert cache.get("versioning:probe", version=settings.CACHE_VERSION + 1) is None
        finally:
            cache.delete("versioning:probe")
