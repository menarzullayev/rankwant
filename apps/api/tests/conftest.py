from __future__ import annotations

import io
import os
from datetime import timedelta
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import pytest
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

from contests.models import Contest, ContestProblem
from core.models import User
from judging.models import Attempt
from judging.provider import InMemoryJudgeProvider, set_provider
from judging.verdicts import Verdict
from problems.models import Language, Problem, ReferenceSolution, TestCase, Validator
from ratings.models import UserSolvedProblem


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


class FakeS3:
    """Xotiradagi S3 — avatar sinovlari MinIO'siz ishlaydi."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put_object(self, **kw: Any) -> None:
        self.objects[kw["Key"]] = kw["Body"]

    def get_object(self, **kw: Any) -> dict[str, Any]:
        return {"Body": io.BytesIO(self.objects[kw["Key"]])}

    def delete_object(self, **kw: Any) -> None:
        self.objects.pop(kw["Key"], None)


@pytest.fixture
def fake_s3(monkeypatch: pytest.MonkeyPatch) -> FakeS3:
    s3 = FakeS3()
    monkeypatch.setattr("core.avatars._client", lambda: s3)
    return s3


@pytest.fixture
def fake_hack_storage(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """S3 o'rniga lug'at: hack testi obyekt xotirasiga yozilmaydi.

    Yozish ham, o'qish ham almashtiriladi — aks holda serializer
    yozilgan kiritmani qaytarib o'qiyolmay, sukut bilan bo'sh berardi
    va ko'rinish testi hech narsani isbotlamasdi.
    """
    saved: dict[str, str] = {}

    def put(key: str, content: str) -> str:
        saved[key] = content
        return f"s3://test/{key}"

    def get(ref: str) -> str:
        return saved[ref.removeprefix("s3://test/")]

    monkeypatch.setattr("problems.storage.put_test_data", put)
    monkeypatch.setattr("problems.storage.get_test_data", get)
    monkeypatch.setattr("problems.storage.ensure_bucket", lambda: None)
    return saved


@pytest.fixture
def defender_attempt(db, problem, language, user, other_user) -> Attempt:
    """Hack qilinadigan holat: ikkala darvoza ochiq, nishon `AC`.

    `user` — hacker (masalani o'zi yechgan), `other_user` — himoyachi.
    """
    Validator.objects.create(problem=problem, language=language, source="int main(){}\n")
    ReferenceSolution.objects.create(problem=problem, language=language, source="int main(){}\n")
    attempt = Attempt.objects.create(
        user=other_user,
        problem=problem,
        language=language,
        source_code="hacked_code",
        verdict=Verdict.AC,
        judged_at=timezone.now(),
    )
    UserSolvedProblem.objects.create(
        user=other_user,
        problem=problem,
        first_ac_attempt=attempt,
        difficulty_at_solve=problem.difficulty,
    )
    # Hisoblagich qatorlar bilan mos bo'lishi SHART: ishlab chiqarishda uni
    # `on_attempt_judged` oshiradi, bu yerda esa qator qo'lda yaratildi.
    # Mos bo'lmasa bekor qilish `solved_count` ni nol ostiga tushirib,
    # butun tranzaksiyani yiqitardi.
    problem.solved_count = 1
    problem.save(update_fields=["solved_count"])
    # Hacker ham masalani yechgan — ADR-0020 ning 2-tamoyili.
    UserSolvedProblem.objects.create(
        user=user, problem=problem, difficulty_at_solve=problem.difficulty
    )
    return attempt
