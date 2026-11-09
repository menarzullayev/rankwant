"""Audit Q-06 (2026-11-10): an expired session's IP and browser row is not kept.

`sessions.live()` pruned one user's rows only when that user opened the
device list, so a row could outlive its session forever. The privacy
policy now says the row lives as long as the session; the daily beat task
`core.prune_dead_sessions` makes that true for every account.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone

from core import sessions
from core.models import UserSession
from core.tasks import prune_dead_sessions

pytestmark = pytest.mark.django_db


def _row(user, key: str, *, expires_in: timedelta | None) -> UserSession:
    if expires_in is not None:
        Session.objects.create(
            session_key=key, session_data="", expire_date=timezone.now() + expires_in
        )
    return UserSession.objects.create(user=user, session_key=key, ip="203.0.113.7", user_agent="x")


def test_expired_and_orphan_rows_are_removed(user) -> None:
    alive = _row(user, "a" * 32, expires_in=timedelta(days=1))
    _row(user, "b" * 32, expires_in=timedelta(days=-1))
    _row(user, "c" * 32, expires_in=None)

    assert prune_dead_sessions() == 2

    assert list(UserSession.objects.values_list("pk", flat=True)) == [alive.pk]


def test_nothing_to_remove_is_a_no_op(user) -> None:
    _row(user, "d" * 32, expires_in=timedelta(hours=1))
    assert sessions.prune_dead() == 0
    assert UserSession.objects.count() == 1


def test_the_task_runs_daily() -> None:
    entry = settings.CELERY_BEAT_SCHEDULE["prune-dead-sessions"]
    assert entry["task"] == "core.prune_dead_sessions"
    assert entry["schedule"] == 86400.0
