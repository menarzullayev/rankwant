from __future__ import annotations

import os
from datetime import timedelta
from urllib.parse import urlsplit, urlunsplit

import pytest
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from contests.models import Contest, ContestProblem
from core.models import User
from judging.provider import InMemoryJudgeProvider, set_provider
from problems.models import Language, Problem, TestCase


@pytest.fixture(autouse=True, scope="session")
def isolated_cache():
    """Har xdist worker'iga alohida Redis DB.

    Quyidagi `clear_throttle_cache` keshni tozalaydi, Redis backendida
    esa `cache.clear()` — FLUSHDB, ya'ni BUTUN bazani. Parallel ishlashda
    bitta worker boshqasining keshini o'rtasida o'chirib yuboradi va
    kesh testlari tasodifiy yiqiladi: o'lchandi — CI da `-n 4` ostida
    `test_kesh_takroriy_s3_o_qishini_yo_qotadi` ikkita chaqiruv kutgan
    joyda to'rttasini ko'rgan.

    Mahalliy ishga tushirishda buni sezib bo'lmasdi: `REDIS_URL` siz
    LocMemCache ishlaydi va u allaqachon har jarayonga alohida.
    """
    worker = os.environ.get("PYTEST_XDIST_WORKER", "")
    location = settings.CACHES["default"].get("LOCATION", "")
    if not worker.startswith("gw") or not str(location).startswith("redis"):
        yield
        return

    parsed = urlsplit(str(location))
    per_worker = urlunsplit(parsed._replace(path=f"/{int(worker[2:]) + 1}"))
    with override_settings(
        CACHES={
            **settings.CACHES,
            "default": {**settings.CACHES["default"], "LOCATION": per_worker},
        }
    ):
        yield


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
