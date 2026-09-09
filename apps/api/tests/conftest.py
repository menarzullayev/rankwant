from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from contests.models import Contest, ContestProblem
from core.models import User
from judging.provider import InMemoryJudgeProvider, set_provider
from problems.models import Language, Problem, TestCase


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """DRF throttling holatini keshda saqlaydi.

    Tozalanmasa, bitta testdagi submitlar keyingi testda 429 keltirib
    chiqaradi va nosozlik testlar TARTIBIGA bog'liq bo'lib qoladi.
    """
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def memory_judge():
    """Testlarda judge navbatga tegmaydi."""
    provider = InMemoryJudgeProvider()
    set_provider(provider)
    yield provider
    set_provider(None)


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(username="aziz", password="Parol!12345")


@pytest.fixture
def other_user(db) -> User:
    return User.objects.create_user(username="bekzod", password="Parol!12345")


@pytest.fixture
def language(db) -> Language:
    return Language.objects.create(
        code="cpp23",
        name="C++",
        version="23",
        compile_cmd=["g++", "-o", "{bin}", "{src}"],
        run_cmd=["{bin}"],
    )


@pytest.fixture
def problem(db) -> Problem:
    """Oddiy ommaviy masala — TESTI BILAN.

    Testsiz masalaga yuborish rad etiladi (judge IE qaytarardi), ya'ni
    testsiz fixture haqiqiy masalani ifodalamaydi. Tartib raqami ataylab
    katta: namuna testlar qo'shadigan fixture'lar 1-dan boshlanadi.
    """
    created = Problem.objects.create(
        slug="a-plus-b",
        title="A+B",
        statement="a va b ni qo'shing",
        difficulty=800,
        is_public=True,
    )
    TestCase.objects.create(
        problem=created, order=10, input_ref="s3://x/10.in", output_ref="s3://x/10.out"
    )
    return created


@pytest.fixture
def hard_problem(db) -> Problem:
    return Problem.objects.create(
        slug="hard-one",
        title="Qiyin",
        statement="…",
        difficulty=2500,
        is_public=True,
    )


@pytest.fixture
def contest(db, problem) -> Contest:
    now = timezone.now()
    c = Contest.objects.create(
        slug="round-1",
        title="Round 1",
        start_at=now - timedelta(hours=2),
        end_at=now - timedelta(minutes=1),
        is_rated=True,
    )
    ContestProblem.objects.create(contest=c, problem=problem, index_letter="A")
    return c
