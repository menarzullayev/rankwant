"""User fields added after the competitor benchmark (ADR-0024).

The stored counters must follow every writer of their source rows, and
`core.user_stats` must derive the same values back. Each test exercises one
writer; `test_services_and_rebuild_agree` ties them together.
"""

from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from django.core.management import CommandError, call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core import prefs, sessions, user_stats
from core.models import User, UserSession
from judging.models import Attempt
from judging.verdicts import Verdict
from problems.models import Language, Problem
from qvant import streak
from ratings.models import RatingHistory, UserSolvedProblem
from ratings.services import bump_max_rating, on_accept_revoked, on_attempt_judged


def kirgan(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def accepted(user: User, problem: Problem, language: Language) -> Attempt:
    attempt = Attempt.objects.create(
        user=user, problem=problem, language=language, source_code="x", verdict=Verdict.AC
    )
    on_attempt_judged(attempt)
    return attempt


def fresh(user: User) -> User:
    return User.objects.get(pk=user.pk)


@pytest.mark.django_db
class TestStoredCounters:
    def test_max_rating_only_rises(self, user: User) -> None:
        bump_max_rating(user, "skills", 1500)
        bump_max_rating(user, "skills", 1000)

        assert fresh(user).max_rating_skills == 1500
        assert user.max_rating_skills == 1500, "the object in memory follows the row"

    def test_skills_history_raises_the_maximum(
        self, user: User, problem: Problem, language: Language
    ) -> None:
        accepted(user, problem, language)

        row = fresh(user)
        assert row.rating_skills > 0
        assert row.max_rating_skills == row.rating_skills

    def test_solved_count_follows_first_ac_and_rejudge(
        self, user: User, problem: Problem, language: Language
    ) -> None:
        first = accepted(user, problem, language)
        accepted(user, problem, language)
        assert fresh(user).solved_count == 1, "only the first AC counts"

        # Rejudge revokes the first AC while the second still stands.
        Attempt.objects.filter(pk=first.pk).update(verdict=Verdict.WA)
        on_accept_revoked(first)
        assert fresh(user).solved_count == 1, "the problem is still solved"

        second = Attempt.objects.exclude(pk=first.pk).get(user=user)
        Attempt.objects.filter(pk=second.pk).update(verdict=Verdict.WA)
        on_accept_revoked(second)
        assert fresh(user).solved_count == 0

    def test_solved_count_never_goes_below_zero(
        self, user: User, problem: Problem, language: Language
    ) -> None:
        attempt = accepted(user, problem, language)
        User.objects.filter(pk=user.pk).update(solved_count=0)  # drifted behind the rows

        Attempt.objects.filter(pk=attempt.pk).update(verdict=Verdict.WA)
        on_accept_revoked(attempt)

        assert fresh(user).solved_count == 0

    def test_streak_max_keeps_the_longest_run(self, user: User) -> None:
        day = date(2026, 9, 1)
        for offset in range(3):
            streak.touch(user, day + timedelta(days=offset))
        streak.touch(user, day + timedelta(days=5))  # the run breaks

        row = fresh(user)
        assert (row.streak_count, row.streak_max) == (1, 3)

    def test_session_record_writes_last_seen_at(self, user: User) -> None:
        request = SimpleNamespace(user=user, session=SimpleNamespace(session_key="k" * 40), META={})

        sessions.record(request, force=True)

        seen = UserSession.objects.get(session_key="k" * 40).last_seen
        assert fresh(user).last_seen_at == seen


@pytest.mark.django_db
class TestRebuild:
    def test_services_and_rebuild_agree(
        self, user: User, problem: Problem, language: Language
    ) -> None:
        accepted(user, problem, language)
        streak.touch(user, timezone.localdate())
        sessions.record(
            SimpleNamespace(user=user, session=SimpleNamespace(session_key="r" * 40), META={}),
            force=True,
        )

        assert user_stats.reconcile(fix=False) == []

    def test_drift_is_reported_and_repaired(
        self, user: User, problem: Problem, language: Language
    ) -> None:
        accepted(user, problem, language)
        User.objects.filter(pk=user.pk).update(solved_count=7, max_rating_skills=None)

        diffs = {(field, stored) for _, field, stored, _ in user_stats.reconcile(fix=False)}
        assert diffs == {("solved_count", 7), ("max_rating_skills", None)}
        with pytest.raises(CommandError):
            call_command("recount_user_stats", "--check")

        call_command("recount_user_stats")

        row = fresh(user)
        assert (row.solved_count, row.max_rating_skills) == (1, row.rating_skills)
        assert user_stats.reconcile(fix=False) == []

    def test_raise_only_columns_are_never_lowered(self, user: User) -> None:
        # A freeze can keep a streak alive without an accepted attempt that day,
        # and signing out deletes the session that recorded the visit.
        seen = timezone.now() - timedelta(days=2)
        User.objects.filter(pk=user.pk).update(streak_max=9, last_seen_at=seen)

        call_command("recount_user_stats")

        row = fresh(user)
        assert (row.streak_max, row.last_seen_at) == (9, seen)

    def test_bulk_fill_matches_the_sources(
        self, user: User, other_user: User, problem: Problem, language: Language
    ) -> None:
        # The migration fills the new columns with `bulk=True`.
        accepted(user, problem, language)
        RatingHistory.objects.create(
            user=other_user,
            rating_type="contest",
            value_before=1400,
            value_after=1520,
            delta=120,
            reason="contest",
        )
        UserSession.objects.create(user=other_user, session_key="b" * 40)
        User.objects.update(solved_count=0, streak_max=0, max_rating_skills=None, last_seen_at=None)

        user_stats.reconcile(fix=True, bulk=True)

        assert fresh(user).solved_count == UserSolvedProblem.objects.filter(user=user).count()
        other = fresh(other_user)
        assert (other.max_rating_contest, other.last_seen_at is not None) == (1520, True)
        assert user_stats.reconcile(fix=False) == []

    def test_longest_run(self) -> None:
        d = date(2026, 1, 1)
        days = [d, d + timedelta(1), d + timedelta(2), d + timedelta(5), d + timedelta(6)]
        assert user_stats.longest_run(days) == 3
        assert user_stats.longest_run([]) == 0


@pytest.mark.django_db
class TestApi:
    def test_public_profile_and_leaderboard(
        self, user: User, other_user: User, problem: Problem, language: Language
    ) -> None:
        accepted(user, problem, language)

        detail = APIClient().get(reverse("user-detail", args=[user.username])).data
        rows = APIClient().get(reverse("user-list"), {"ordering": "-solved_count"}).data
        order = [row["username"] for row in rows["results"]]

        # The first AC also starts a streak (`qvant.streak.touch`).
        assert (detail["solved_count"], detail["streak_max"]) == (1, 1)
        assert order.index(user.username) < order.index(other_user.username)

    def test_me_saves_names_and_shirt_size(self, user: User) -> None:
        response = kirgan(user).patch(
            reverse("me"),
            {"first_name": "  Ali \t Valiyev ", "last_name": "Karimov", "shirt_size": "XL"},
            format="json",
        )

        assert response.status_code == 200, response.data
        row = fresh(user)
        assert (row.first_name, row.last_name, row.shirt_size) == ("Ali Valiyev", "Karimov", "XL")

    def test_me_rejects_bad_names_and_sizes(self, user: User) -> None:
        name = kirgan(user).patch(reverse("me"), {"first_name": "Ali\x00"}, format="json")
        size = kirgan(user).patch(reverse("me"), {"shirt_size": "XXXXL"}, format="json")

        assert (name.status_code, size.status_code) == (400, 400)

    def test_me_patch_does_not_overwrite_concurrent_counters(self, user: User) -> None:
        # The judge worker updates the row after the request has read it.
        User.objects.filter(pk=user.pk).update(solved_count=5, rating_skills=900)

        response = kirgan(user).patch(reverse("me"), {"bio": "salom"}, format="json")

        assert response.status_code == 200
        row = fresh(user)
        assert (row.bio, row.solved_count, row.rating_skills) == ("salom", 5, 900)

    def test_dormant_fields_are_not_exposed(self, user: User) -> None:
        me = kirgan(user).get(reverse("me")).data
        public = APIClient().get(reverse("user-detail", args=[user.username])).data

        dormant = {"plan", "postal_address", "device_fingerprint", "coach_can_view_attempts"}
        assert not dormant & set(me)
        assert not dormant & set(public)
        assert "shirt_size" not in public, "owner-only, like phone"


class TestProblemsetPrefs:
    def test_accepted(self) -> None:
        clean = prefs.validate({"problemset": {"hideTags": True, "hideSolved": False}})
        assert clean["problemset"] == {"hideTags": True, "hideSolved": False}

    @pytest.mark.parametrize(
        "value",
        [{"hideTags": "yes"}, {"showAll": True}, ["hideTags"]],
    )
    def test_rejected(self, value: object) -> None:
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"problemset": value})
