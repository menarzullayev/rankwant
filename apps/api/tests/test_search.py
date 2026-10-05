"""Site search — one endpoint, one way of matching (see `core.search`)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from arena.models import ArenaRound
from blog.models import Post
from content.models import Article, Roadmap
from core import search as site_search
from core.models import User
from hackathons.models import Hackathon
from problems.models import Problem, Topic
from quizzes.models import Quiz
from tournaments.models import Tournament
from updates.models import SystemUpdate


def find(q: str, **params: Any) -> dict[str, Any]:
    response = APIClient().get(reverse("search"), {"q": q, **params})
    assert response.status_code == 200
    body: dict[str, Any] = response.json()
    return body


def hits(body: dict[str, Any], kind_of: str) -> list[dict[str, Any]]:
    for group in body["groups"]:
        if group["type"] == kind_of:
            found: list[dict[str, Any]] = group["results"]
            return found
    return []


def keys(body: dict[str, Any], kind_of: str) -> list[str]:
    return [hit["key"] for hit in hits(body, kind_of)]


@pytest.mark.django_db
class TestShape:
    def test_a_short_query_asks_nothing(self, problem) -> None:
        body = find("a")
        assert body["groups"] == []
        assert body["total"] == 0
        assert set(body["counts"]) == set(site_search.TYPES)

    def test_every_registered_type_has_a_source(self) -> None:
        assert {source.type for source in site_search.sources()} == set(site_search.TYPES)

    def test_groups_only_list_types_that_matched(self, problem, contest) -> None:
        body = find("round")
        assert [group["type"] for group in body["groups"]] == ["contest"]
        assert body["counts"]["contest"] == 1
        assert body["counts"]["problem"] == 0

    def test_a_hit_says_what_it_is(self, problem) -> None:
        hit = hits(find("a+b"), "problem")[0]
        assert hit["type"] == "problem"
        assert hit["kind"] == "problem"
        assert hit["key"] == "a-plus-b"
        assert hit["title"] == "A+B"
        assert hit["meta"] == 800


@pytest.mark.django_db
class TestCoverage:
    """Every kind the palette promises is reachable through the endpoint."""

    def test_users_by_username_and_by_name(self, user) -> None:
        User.objects.filter(pk=user.pk).update(display_name="Aziz Karimov")
        assert keys(find("azi"), "user") == ["aziz"]
        assert keys(find("karimov"), "user") == ["aziz"]

    def test_inactive_users_stay_out(self, user) -> None:
        User.objects.filter(pk=user.pk).update(is_active=False)
        assert keys(find("aziz"), "user") == []

    def test_topics(self, db) -> None:
        Topic.objects.create(slug="dp", name_uz="Dinamik dasturlash", name_en="Dynamic programming")
        assert keys(find("dinamik"), "topic") == ["dp"]
        assert keys(find("dynamic"), "topic") == ["dp"]
        assert keys(find("dp"), "topic") == ["dp"]

    def test_every_competition_format(self, contest) -> None:
        now = timezone.now()
        ArenaRound.objects.create(slug="arena-kuz", title="Kuz arenasi", start_at=now)
        Tournament.objects.create(
            slug="turnir-kuz", title="Kuz turniri", start_at=now, end_at=now + timedelta(days=1)
        )
        Hackathon.objects.create(
            slug="xakaton-kuz",
            title="Kuz xakatoni",
            start_at=now,
            submission_deadline=now + timedelta(days=1),
            end_at=now + timedelta(days=2),
        )
        found = {hit["kind"]: hit["key"] for hit in hits(find("kuz"), "contest")}
        assert found == {
            "arena": "arena-kuz",
            "tournament": "turnir-kuz",
            "hackathon": "xakaton-kuz",
        }
        assert keys(find("round"), "contest") == [contest.slug]

    def test_learning_content(self, db) -> None:
        Article.objects.create(slug="graf", title="Graf asoslari", body="x", is_published=True)
        Article.objects.create(
            slug="bfs",
            title="Graf bo'ylab BFS",
            body="x",
            is_published=True,
            kind=Article.Kind.ALGORITHM,
        )
        Roadmap.objects.create(slug="graf-yoli", title="Graf yo'li", is_published=True)
        Quiz.objects.create(slug="graf-testi", title="Graf testi", is_published=True)
        found = {hit["kind"]: hit["key"] for hit in hits(find("graf", limit=10), "learn")}
        assert found == {
            "article": "graf",
            "algorithm": "bfs",
            "roadmap": "graf-yoli",
            "quiz": "graf-testi",
        }

    def test_news_and_changes(self, db) -> None:
        Post.objects.create(
            slug="yangi", title="Sozlamalar yangilandi", body="x", is_published=True
        )
        update = SystemUpdate.objects.create(
            title="Sozlamalar qayta qurildi",
            kind=SystemUpdate.Kind.IMPROVED,
            module=SystemUpdate.Module.CORE,
            status=SystemUpdate.Status.PUBLISHED,
            released_at=timezone.now().date(),
        )
        found = {hit["kind"]: hit["key"] for hit in hits(find("sozlamalar"), "news")}
        assert found == {"post": "yangi", "update": str(update.pk)}

    def test_drafts_stay_out(self, db) -> None:
        Article.objects.create(slug="qoralama", title="Maxfiy qoralama", body="x")
        Post.objects.create(slug="qoralama-post", title="Maxfiy qoralama", body="x")
        Quiz.objects.create(slug="qoralama-test", title="Maxfiy qoralama")
        SystemUpdate.objects.create(
            title="Maxfiy qoralama",
            kind=SystemUpdate.Kind.NEW,
            module=SystemUpdate.Module.CORE,
            released_at=timezone.now().date(),
        )
        Problem.objects.create(slug="yopiq", title="Maxfiy qoralama", statement="x", difficulty=800)
        ArenaRound.objects.create(
            slug="yopiq-arena", title="Maxfiy qoralama", start_at=timezone.now(), is_public=False
        )
        assert find("maxfiy")["total"] == 0


@pytest.mark.django_db
class TestMatching:
    def test_the_apostrophe_form_does_not_matter(self, problem) -> None:
        """An Uzbek keyboard types `ʻ` or `’`; the database stores `'`."""
        Problem.objects.create(
            slug="nol-ga-bolish",
            title="0 ga bo'lish",
            statement="x",
            difficulty=800,
            is_public=True,
        )
        for mark in ("'", "ʻ", "’", "‘", ""):
            assert keys(find(f"ga bo{mark}lish"), "problem") == ["nol-ga-bolish"], mark

    def test_the_same_folding_reaches_every_type(self, user) -> None:
        """Before, only problems were folded; the rest matched the raw text."""
        User.objects.filter(pk=user.pk).update(display_name="O'ktam To'rayev")
        Article.objects.create(slug="yigindi", title="Yig'indi", body="x", is_published=True)
        assert keys(find("oktam"), "user") == ["aziz"]
        assert keys(find("toʻrayev"), "user") == ["aziz"]
        assert keys(find("yigindi"), "learn") == ["yigindi"]
        assert keys(find("yig’indi"), "learn") == ["yigindi"]

    def test_rank_exact_then_prefix_then_word_then_inside(self, db) -> None:
        for slug, title in (
            ("d", "Katta graflar"),
            ("c", "Daraxt va graf"),
            ("b", "Grafda yurish"),
            ("a", "Graf"),
            ("e", "Paragraf"),
        ):
            Problem.objects.create(
                slug=slug, title=title, statement="x", difficulty=800, is_public=True
            )
        assert keys(find("graf", type="problem"), "problem") == ["a", "b", "d", "c", "e"]

    def test_a_secondary_field_match_ranks_last(self, db) -> None:
        Post.objects.create(
            slug="izoh", title="Boshqa narsa", summary="Reyting haqida", body="x", is_published=True
        )
        Post.objects.create(slug="sarlavha", title="Reyting formulasi", body="x", is_published=True)
        assert keys(find("reyting"), "news") == ["sarlavha", "izoh"]

    def test_like_wildcards_are_literal(self, problem) -> None:
        assert find("%%")["total"] == 0
        assert find("__")["total"] == 0

    def test_short_needles_on_users_are_prefixes(self, user, other_user) -> None:
        """Two characters cannot use the trigram index for a substring, and
        the user table is too large to scan — so they match from the start."""
        assert keys(find("az"), "user") == ["aziz"]
        assert keys(find("zi"), "user") == []
        assert keys(find("ziz"), "user") == ["aziz"]

    @pytest.mark.skipif(
        connection.vendor != "postgresql", reason="trigram similarity is PostgreSQL"
    )
    def test_a_typo_still_finds_it(self, db) -> None:
        Article.objects.create(slug="algo", title="Algoritm asoslari", body="x", is_published=True)
        body = find("algortm")
        assert keys(body, "learn") == ["algo"]
        assert body["groups"][0]["fuzzy"] is True

    @pytest.mark.skipif(
        connection.vendor != "postgresql", reason="trigram similarity is PostgreSQL"
    )
    def test_an_exact_match_is_not_diluted_with_guesses(self, db) -> None:
        Article.objects.create(slug="algo", title="Algoritm asoslari", body="x", is_published=True)
        Article.objects.create(slug="alg2", title="Algorifm tarixi", body="x", is_published=True)
        body = find("algoritm")
        assert keys(body, "learn") == ["algo"]
        assert body["groups"][0]["fuzzy"] is False


@pytest.mark.django_db
class TestPaging:
    @pytest.fixture
    def many(self, db) -> None:
        Problem.objects.bulk_create(
            Problem(
                slug=f"graf-{n:02d}",
                title=f"Graf {n:02d}",
                title_search=f"graf {n:02d}",
                statement="x",
                difficulty=800 + n,
                is_public=True,
            )
            for n in range(30)
        )

    def test_the_palette_takes_a_few_of_each(self, many) -> None:
        body = find("graf")
        assert len(hits(body, "problem")) == site_search.GROUP_LIMIT_DEFAULT
        assert body["counts"]["problem"] == 30

    def test_one_type_is_paged(self, many) -> None:
        first = keys(find("graf", type="problem", limit=10), "problem")
        second = keys(find("graf", type="problem", limit=10, offset=10), "problem")
        assert first == [f"graf-{n:02d}" for n in range(10)]
        assert second == [f"graf-{n:02d}" for n in range(10, 20)]

    def test_a_single_type_still_counts_the_others(self, many) -> None:
        Topic.objects.create(slug="graflar", name_uz="Graflar")
        body = find("graf", type="topic")
        assert [group["type"] for group in body["groups"]] == ["topic"]
        assert body["counts"]["problem"] == 30

    def test_limits_are_clamped(self, many) -> None:
        assert len(hits(find("graf", limit=999), "problem")) == site_search.GROUP_LIMIT_MAX
        assert len(hits(find("graf", type="problem", limit=999), "problem")) == 30
        assert find("graf", type="problem", limit="x", offset="-4")["groups"][0]["count"] == 30

    def test_an_unknown_type_means_all(self, many) -> None:
        assert find("graf", type="nonsense")["type"] == "all"


class TestFolding:
    def test_every_apostrophe_form_folds_away(self) -> None:
        for mark in site_search.APOSTROPHES:
            assert site_search.normalize_search(f"bo{mark}lish") == "bolish"
        assert site_search.normalize_search("  Ikki   SO'Z ") == "ikki soz"
