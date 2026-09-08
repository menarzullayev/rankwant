"""Masala sahifasidagi namuna testlar.

Namunasiz kirish formatini matndan tushunib bo'lmaydi — RoboContest,
KEP va Codeforces uchalasida ham ular masala sahifasining bir qismi.
Ma'lumot DB da emas, S3 da (05-domain-model), shuning uchun bu yerda
o'qish, keshlash va S3 yiqilgandagi xatti-harakat tekshiriladi.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from problems import storage
from problems.models import TestCase as ProblemTestCase


@pytest.fixture
def staff_client(db) -> APIClient:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff-samples", is_staff=True))
    return client


@pytest.fixture
def samples(problem, monkeypatch) -> None:
    contents = {
        "s3://rankwant/tests/a-plus-b/1.in": "2 3\n",
        "s3://rankwant/tests/a-plus-b/1.out": "5\n",
        "s3://rankwant/tests/a-plus-b/2.in": "10 20\n",
        "s3://rankwant/tests/a-plus-b/2.out": "30\n",
    }
    for order in (1, 2):
        ProblemTestCase.objects.create(
            problem=problem,
            order=order,
            input_ref=f"s3://rankwant/tests/a-plus-b/{order}.in",
            output_ref=f"s3://rankwant/tests/a-plus-b/{order}.out",
            is_sample=order == 1,
        )
    monkeypatch.setattr(storage, "get_test_data", lambda ref: contents[ref])
    cache.delete(storage.samples_cache_key(problem.slug))


def test_faqat_namuna_testlar_qaytadi(samples, problem) -> None:
    response = APIClient().get(reverse("problem-detail", args=[problem.slug]))

    assert response.status_code == 200
    # 2-test namuna emas — javob ochiq sahifada ko'rinmasligi kerak.
    assert response.data["samples"] == [{"order": 1, "input": "2 3\n", "expected": "5\n"}]


def test_s3_yiqilsa_sahifa_baribir_ochiladi(samples, problem, monkeypatch) -> None:
    def boom(ref: str) -> str:
        raise OSError("S3 javob bermadi")

    monkeypatch.setattr(storage, "get_test_data", boom)

    response = APIClient().get(reverse("problem-detail", args=[problem.slug]))

    assert response.status_code == 200
    assert response.data["samples"] == []
    assert response.data["statement"]


def test_kesh_takroriy_s3_o_qishini_yo_qotadi(samples, problem) -> None:
    calls: list[str] = []
    original = storage.get_test_data

    def counted(ref: str) -> str:
        calls.append(ref)
        return original(ref)

    storage.get_test_data = counted  # type: ignore[assignment]
    try:
        url = reverse("problem-detail", args=[problem.slug])
        APIClient().get(url)
        first = len(calls)
        APIClient().get(url)
        assert len(calls) == first, "ikkinchi so'rov keshdan olinishi kerak"
    finally:
        storage.get_test_data = original  # type: ignore[assignment]


def test_test_yuklanganda_kesh_tozalanadi(samples, problem, staff_client, monkeypatch) -> None:
    url = reverse("problem-detail", args=[problem.slug])
    APIClient().get(url)  # keshni to'ldiradi

    monkeypatch.setattr(storage, "ensure_bucket", lambda: None)
    monkeypatch.setattr(storage, "put_test_data", lambda key, content: f"s3://rankwant/{key}")
    monkeypatch.setattr(
        storage, "get_test_data", lambda ref: "7 8\n" if ref.endswith(".in") else "15\n"
    )

    staff_client.post(
        reverse("staff-problem-tests", args=[problem.slug]),
        {"order": 1, "input": "7 8\n", "expected": "15\n", "is_sample": True, "points": 0},
        format="json",
    )

    assert APIClient().get(url).data["samples"] == [
        {"order": 1, "input": "7 8\n", "expected": "15\n"}
    ]


def test_yechilgan_masala_royxatda_belgilanadi(problem, user) -> None:
    from ratings.models import UserSolvedProblem

    url = reverse("problem-list")
    client = APIClient()

    assert client.get(url).data["results"][0]["is_solved"] is False, "mehmonga false"

    client.force_authenticate(user)
    assert client.get(url).data["results"][0]["is_solved"] is False

    UserSolvedProblem.objects.create(
        user=user, problem=problem, difficulty_at_solve=problem.difficulty
    )
    assert client.get(url).data["results"][0]["is_solved"] is True


def test_sevimlilar_qo_shiladi_va_olib_tashlanadi(problem, user) -> None:
    client = APIClient()
    url = reverse("problem-favourite", args=[problem.slug])
    detail = reverse("problem-detail", args=[problem.slug])

    assert client.post(url).status_code in (401, 403), "mehmon belgilay olmaydi"

    client.force_authenticate(user)
    assert client.post(url).data["is_favourite"] is True
    assert client.get(detail).data["is_favourite"] is True
    # Takroriy POST xato bermaydi — tugma ikki marta bosilishi mumkin.
    assert client.post(url).data["is_favourite"] is True

    assert client.delete(url).data["is_favourite"] is False
    assert client.get(detail).data["is_favourite"] is False


def test_baho_ozgartiriladi_va_ortacha_hisoblanadi(problem, user, other_user) -> None:
    url = reverse("problem-rate", args=[problem.slug])
    client = APIClient()

    client.force_authenticate(user)
    assert client.post(url, {"score": 5}, format="json").data["average"] == 5.0
    # Qayta baholash yangi yozuv emas, o'zgartirish.
    body = client.post(url, {"score": 3}, format="json").data
    assert (body["average"], body["count"]) == (3.0, 1)
    assert client.post(url, {"score": 9}, format="json").status_code == 400

    client.force_authenticate(other_user)
    assert client.post(url, {"score": 5}, format="json").data == {
        "average": 4.0,
        "count": 2,
        "my_rating": 5,
    }

    detail = APIClient().get(reverse("problem-detail", args=[problem.slug]))
    assert detail.data["rating"] == {"average": 4.0, "count": 2}
    assert detail.data["my_rating"] is None, "mehmonda o'z bahosi yo'q"


class TestProblemCode:
    """Ommaviy raqam — `#0431`. Berilgach o'zgarmaydi va qayta ishlatilmaydi."""

    def test_qoralamaga_raqam_berilmaydi(self, db) -> None:
        from problems.models import Problem

        draft = Problem.objects.create(
            slug="qoralama", title="Qoralama", statement="…", difficulty=800, is_public=False
        )
        assert draft.code is None

    def test_elon_qilinganda_raqam_beriladi(self, db, problem) -> None:
        from problems.models import Problem

        assert problem.code is not None

        draft = Problem.objects.create(
            slug="ikkinchi", title="Ikkinchi", statement="…", difficulty=900, is_public=False
        )
        draft.is_public = True
        draft.save()
        draft.refresh_from_db()

        assert draft.code == problem.code + 1

    def test_raqam_ochirilgandan_keyin_qayta_ishlatilmaydi(self, db, problem) -> None:
        from problems.models import Problem

        first = problem.code
        second = Problem.objects.create(
            slug="uchinchi", title="Uchinchi", statement="…", difficulty=900, is_public=True
        )
        assert second.code == first + 1

        second.delete()
        third = Problem.objects.create(
            slug="tortinchi", title="To'rtinchi", statement="…", difficulty=900, is_public=True
        )
        # Teshik qoladi — bu ataylab: tarqalgan raqam boshqa masalaga o'tmasin.
        assert third.code == first + 2

    def test_qayta_saqlash_raqamni_ozgartirmaydi(self, db, problem) -> None:
        original = problem.code
        problem.title = "Boshqa nom"
        problem.save()
        problem.refresh_from_db()
        assert problem.code == original


def test_royxat_qator_soniga_qarab_sorov_kopaytirmaydi(
    db, user, problem, hard_problem, django_assert_num_queries
) -> None:
    """Sevimli, baho va oxirgi urinish — guruh so'rovlar bilan.

    Qator ortganda so'rov soni o'zgarmasligi kerak; aks holda 100 masalali
    sahifa 300 ta so'rov qilardi.
    """
    from problems.models import Favourite

    client = APIClient()
    client.force_authenticate(user)
    Favourite.objects.create(user=user, problem=problem)

    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    url = reverse("problem-list")
    with CaptureQueriesContext(connection) as ctx:
        client.get(url)
    baseline = len(ctx.captured_queries)

    from problems.models import Problem

    for i in range(8):
        Problem.objects.create(
            slug=f"yuk-{i}", title=f"Yuk {i}", statement="…", difficulty=1000, is_public=True
        )

    with django_assert_num_queries(baseline):
        client.get(url)
