"""Which problems are judged on hidden tests (audit Q-05, 2026-11-10).

A problem whose every test is a sample accepts a program that prints the
sample answers. Measured 2026-11-10: 1 225 of 1 236 public problems (the
imported archive) had no hidden test. They stay in the archive, marked,
but a solve there earns neither Skills nor Qvant — otherwise both would
reward a printed sample.

Publishing a problem without hidden tests is already refused
(`staff_serializers`, unconditionally), so this only concerns problems
that were public before that rule.

Other apps import these helpers, never `problems.models` (D7 boundary).
"""

from __future__ import annotations

from django.db.models import Exists, OuterRef

from .models import TestCase


def hidden_tests_exist(problem_ref: str = "pk") -> Exists:
    """`Exists` expression: the problem behind `problem_ref` has a hidden test.

    `problem_ref` names the outer column holding the problem id — `"pk"` on
    a `Problem` queryset, `"problem_id"` on rows that point at a problem.
    """
    return Exists(TestCase.objects.filter(problem_id=OuterRef(problem_ref), is_sample=False))


def any_tests_exist(problem_ref: str = "pk") -> Exists:
    """`Exists` expression: the problem has at least one test of any kind."""
    return Exists(TestCase.objects.filter(problem_id=OuterRef(problem_ref)))


def has_hidden_tests(problem_id: int) -> bool:
    return TestCase.objects.filter(problem_id=problem_id, is_sample=False).exists()


def has_any_tests(problem_id: int) -> bool:
    return TestCase.objects.filter(problem_id=problem_id).exists()


def hidden_test_count(problem_id: int) -> int:
    return TestCase.objects.filter(problem_id=problem_id, is_sample=False).count()
