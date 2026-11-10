"""Audit Q-07.4 (2026-11-10): linked external ratings are refreshed daily.

A rating used to change only when its owner pressed Refresh.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.conf import settings
from django.utils import timezone

from core.models import User
from profiles import tasks
from profiles.models import ExternalProfile

pytestmark = pytest.mark.django_db


@pytest.fixture
def queued(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []

    def fake_apply_async(args: tuple[Any, ...], countdown: int = 0) -> None:
        calls.append(args[0])

    monkeypatch.setattr(tasks.refresh_external, "apply_async", fake_apply_async)
    return calls


def _profile(user: User, kind: str, fetched_ago: timedelta | None) -> ExternalProfile:
    fetched = timezone.now() - fetched_ago if fetched_ago is not None else None
    return ExternalProfile.objects.create(
        user=user, kind=kind, handle="tourist", fetched_at=fetched
    )


def test_only_stale_profiles_of_active_users_are_queued(user, other_user, queued) -> None:
    never = _profile(user, "codeforces", None)
    old = _profile(other_user, "codeforces", timedelta(days=2))
    fresh_user = User.objects.create_user("fresh-q07", password="x")
    _profile(fresh_user, "codeforces", timedelta(hours=1))
    gone = User.objects.create_user("gone-q07", password="x", is_active=False)
    _profile(gone, "codeforces", None)

    assert tasks.refresh_stale_externals() == 2
    assert queued == [never.pk, old.pk]


def test_platforms_without_a_rating_are_skipped(user, queued) -> None:
    _profile(user, "github", None)
    assert tasks.refresh_stale_externals() == 0
    assert queued == []


def test_the_task_runs_daily() -> None:
    entry = settings.CELERY_BEAT_SCHEDULE["refresh-stale-externals"]
    assert entry["task"] == "profiles.refresh_stale_externals"
    assert entry["schedule"] == 86400.0
