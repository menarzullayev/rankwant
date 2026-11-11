"""The algorithms library over the API (ADR-0062, stage 3)."""

from __future__ import annotations

from pathlib import Path

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from content.cpuz import import_library
from content.models import Article, ArticleProblemLink
from problems.models import Problem, Topic
from tests.test_cpuz_import import small_snapshot

IDS = ["algebra--binary-exp", "graph--breadth-first-search"]


@pytest.fixture
def library(tmp_path: Path) -> list[Article]:
    cache.clear()
    Topic.objects.create(slug="ikkilik-daraja", name_uz="Ikkilik daraja")
    Topic.objects.create(slug="graflar-nazariyasi", name_uz="Graflar")
    import_library(root=small_snapshot(tmp_path, IDS))
    Article.objects.filter(source_ref__in=IDS).update(is_published=True)
    return [Article.objects.get(source_ref=i) for i in IDS]


def problem(slug: str, code: int, difficulty: int = 1000, **extra: object) -> Problem:
    return Problem.objects.create(
        slug=slug,
        title=slug,
        code=code,
        statement="x",
        difficulty=difficulty,
        is_public=True,
        **extra,
    )


@pytest.mark.django_db
class TestLibrary:
    def test_the_catalogue_is_one_answer_in_order(self, library: list[Article]) -> None:
        Article.objects.create(slug="bizniki", title="Bizniki", body="x", is_published=True)
        rows = APIClient().get(reverse("article-library")).json()
        assert [r["slug"] for r in rows] == ["binary-exp", "breadth-first-search"]
        assert rows[0]["category"] == "algebra" and rows[0]["level"] == "beginner"
        assert rows[0]["locale"] == "uz"

    def test_english_readers_get_the_original_titles(self, library: list[Article]) -> None:
        rows = APIClient().get(reverse("article-library"), {"lang": "en"}).json()
        assert rows[0]["title"] == "Binary Exponentiation"
        assert rows[0]["locale"] == "en"

    def test_filters_by_category_and_level(self, library: list[Article]) -> None:
        body = APIClient().get(reverse("article-list"), {"category": "graph"}).json()
        assert [r["slug"] for r in body["results"]] == ["breadth-first-search"]
        body = APIClient().get(reverse("article-list"), {"level": "beginner"}).json()
        assert "binary-exp" in [r["slug"] for r in body["results"]]


@pytest.mark.django_db
class TestArticlePage:
    def test_it_carries_the_attribution_and_the_review(self, library: list[Article]) -> None:
        body = APIClient().get(reverse("article-detail", args=["binary-exp"])).json()
        assert body["attribution"]["url"] == "https://cp-algorithms.com/algebra/binary-exp.html"
        assert body["attribution"]["license"] == "CC-BY-SA-4.0"
        assert body["attribution"]["translator"]
        assert body["review"] == {"state": "pending", "changes": 0}
        assert body["original"] is False
        assert body["idea"] and body["complexity"]
        assert any(link["url"].startswith("http") for link in body["external_links"])

    def test_english_readers_read_the_original(self, library: list[Article]) -> None:
        body = (
            APIClient().get(reverse("article-detail", args=["binary-exp"]), {"lang": "en"}).json()
        )
        assert body["title"] == "Binary Exponentiation"
        assert body["locale"] == "en" and body["original"] is True
        assert body["body"].startswith("# Binary Exponentiation")

    def test_our_own_article_has_no_attribution(self) -> None:
        Article.objects.create(slug="bizniki", title="Bizniki", body="x", is_published=True)
        body = APIClient().get(reverse("article-detail", args=["bizniki"])).json()
        assert body["attribution"] is None and body["review"] is None and body["original"] is False

    def test_practice_here_has_three_layers_in_order(self, library: list[Article]) -> None:
        article = library[0]
        picked = problem("tanlangan", 1)
        ArticleProblemLink.objects.create(article=article, problem=picked, role="practice")
        link = article.external_links.first()
        assert link is not None
        problem("ayni-manba", 2, source_url=link.url)
        near = problem("mavzu-yaqin", 3, difficulty=1000)
        far = problem("mavzu-uzoq", 4, difficulty=3000)
        for p in (near, far):
            p.topics.add(Topic.objects.get(slug="ikkilik-daraja"))
        hidden = problem("yopiq", 5)
        hidden.is_public = False
        hidden.save()
        hidden.topics.add(Topic.objects.get(slug="ikkilik-daraja"))
        cache.clear()
        rows = (
            APIClient().get(reverse("article-detail", args=["binary-exp"])).json()["practice_here"]
        )
        assert [(r["slug"], r["via"]) for r in rows] == [
            ("tanlangan", "pick"),
            ("ayni-manba", "source"),
            ("mavzu-yaqin", "topic"),
            ("mavzu-uzoq", "topic"),
        ]


@pytest.mark.django_db
def test_the_glossary_is_served_with_unique_anchors() -> None:
    rows = APIClient().get(reverse("article-glossary")).json()
    assert len(rows) == 174
    slugs = [row["slug"] for row in rows]
    assert len(set(slugs)) == len(slugs)
    algorithm = next(row for row in rows if row["english"] == "Algorithm")
    assert (
        algorithm["slug"] == "algorithm" and algorithm["term"] == "Algoritm" and algorithm["note"]
    )
