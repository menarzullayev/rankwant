"""Recount Skills when a problem crosses the hidden-test line (audit Q-05).

Skills counts only problems judged on hidden tests. When a samples-only
problem gets its first hidden test (a staff upload, or a successful hack
that adds its test), or loses its last one, the solvers' Skills changes
without any action of theirs — ADR-0007 recounts and notifies them.

Every write path for tests goes through `save()` or a queryset `delete()`
(staff upload, hacks, seeders, the KEP importer), and both send these
signals. A `bulk_create` would not: there is none today.
"""

from __future__ import annotations

import logging
from functools import partial
from typing import Any

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Problem, TestCase
from .testsets import hidden_test_count

log = logging.getLogger(__name__)


def _recount_solvers(problem_id: int) -> None:
    from ratings.tasks import recalc_skills_for_problem_task

    recalc_skills_for_problem_task.delay(problem_id)


def _maybe_crossed(problem_id: int) -> None:
    """Zero or one hidden test left means this write may have crossed the line.

    Recounting is idempotent (`recalc_skills` writes only on a change), so
    the rare false positive — editing the only hidden test — costs one
    pass over the solvers; the uploads in between (2, 3, … hidden tests)
    cost nothing.
    """
    if hidden_test_count(problem_id) > 1:
        return
    # `solvers` — the reverse of `UserSolvedProblem.problem`; going through
    # `Problem` keeps `ratings.models` out of this app (D7 boundary).
    if not Problem.objects.filter(pk=problem_id, solvers__isnull=False).exists():
        return
    transaction.on_commit(partial(_recount_solvers, problem_id), robust=True)


@receiver(post_save, sender=TestCase, dispatch_uid="q05_hidden_test_saved")
def _test_saved(sender: type[TestCase], instance: TestCase, **_: Any) -> None:
    _maybe_crossed(instance.problem_id)


@receiver(post_delete, sender=TestCase, dispatch_uid="q05_hidden_test_deleted")
def _test_deleted(sender: type[TestCase], instance: TestCase, **_: Any) -> None:
    if instance.is_sample:
        return
    _maybe_crossed(instance.problem_id)


# ADR-0058: translated titles feed the site search through one stored column.
def _translation_changed(sender: Any, instance: Any, **kwargs: Any) -> None:
    from problems import translations

    translations.on_change(sender, instance, **kwargs)


def _connect_translations() -> None:
    from problems.models import ProblemTranslation

    post_save.connect(
        _translation_changed, sender=ProblemTranslation, dispatch_uid="problem-translation-save"
    )
    post_delete.connect(
        _translation_changed, sender=ProblemTranslation, dispatch_uid="problem-translation-delete"
    )


_connect_translations()
