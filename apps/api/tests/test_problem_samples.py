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
