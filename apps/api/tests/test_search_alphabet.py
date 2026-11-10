"""Search folds the old and the new Uzbek alphabet together (ADR-0059)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from core.search import Fold, normalize_search
from problems.models import Problem

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "text",
    ["O'zbekiston", "Oʻzbekiston", "Özbekiston", "ÖZBEKISTON", "Ozbekiston"],
)
def test_one_fold_for_both_alphabets(text: str) -> None:
    assert normalize_search(text) == "ozbekiston"


def test_digraphs_and_tutuq_fold() -> None:
    assert normalize_search("Çiqiş maʼlumoti") == normalize_search("Chiqish ma'lumoti")
    assert normalize_search("Şart") == "shart"


def test_the_database_fold_matches_python() -> None:
    user = User.objects.create_user("alifbo", password="x", display_name="Şahzod Öğilov")
    folded = User.objects.filter(pk=user.pk).annotate(f=Fold("display_name")).get().f
    assert folded == normalize_search("Şahzod Öğilov") == "shahzod ogilov"


def _keys(query: str) -> list[str]:
    body = APIClient().get(reverse("search"), {"q": query}).json()
    groups = {group["type"]: group for group in body["groups"]}
    return [hit["key"] for hit in groups.get("problem", {}).get("results", [])]


@pytest.mark.parametrize("query", ["yiğindi", "yig'indi", "yigʻindi", "yigindi"])
def test_an_old_title_is_found_in_either_alphabet(query: str) -> None:
    Problem.objects.create(
        slug="alifbo-old", title="Sonlar yig'indisi", statement="x", difficulty=800, is_public=True
    )
    assert "alifbo-old" in _keys(query)


@pytest.mark.parametrize("query", ["şart", "shart", "Shart"])
def test_a_new_title_is_found_in_either_alphabet(query: str) -> None:
    Problem.objects.create(
        slug="alifbo-new", title="Şart va çiqiş", statement="x", difficulty=800, is_public=True
    )
    assert "alifbo-new" in _keys(query)
