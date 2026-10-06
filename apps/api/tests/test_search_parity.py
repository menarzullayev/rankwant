"""Search: what the comparison with Robocontest and KEP found missing."""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from blog.models import Post
from content.models import Article
from core import search as site_search
from core.models import User
from core.throttling import SearchRateThrottle
from problems.models import Problem
from qvant.models import ShopItem
from roadmap.models import RoadmapItem
from updates.models import SystemUpdate, SystemUpdateTranslation


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


@pytest.fixture
def numbered(db) -> Problem:
    return Problem.objects.create(
        slug="toliq-qism-graf",
        title="To'la qism graf",
        statement="x",
        difficulty=2000,
        is_public=True,
        code=1519,
    )


@pytest.mark.django_db
class TestProblemNumber:
    """KEP prints «1519. Complete subgraph»; people type the number."""

    def test_the_number_finds_the_problem(self, numbered) -> None:
        body = find("1519")
        assert keys(body, "problem") == ["toliq-qism-graf"]
        assert hits(body, "problem")[0]["code"] == 1519

    def test_with_the_hash_sign_too(self, numbered) -> None:
        assert keys(find("#1519"), "problem") == ["toliq-qism-graf"]

    def test_the_numbered_problem_comes_before_a_title_that_contains_the_digits(
        self, numbered
    ) -> None:
        Problem.objects.create(
            slug="yil-1519", title="1519-yil", statement="x", difficulty=800, is_public=True
        )
        assert keys(find("1519", type="problem"), "problem") == ["toliq-qism-graf", "yil-1519"]

    def test_a_one_digit_number_is_answered_by_the_lookup_alone(self, db) -> None:
        """`7` is too short to match as text, but it names a problem."""
        Problem.objects.create(
            slug="yettinchi",
            title="Yettinchi",
            statement="x",
            difficulty=800,
            is_public=True,
            code=7,
        )
        Problem.objects.create(
            slug="sarlavhada-7", title="7 ta son", statement="x", difficulty=800, is_public=True
        )
        for query in ("7", "#7"):
            body = find(query)
            assert keys(body, "problem") == ["yettinchi"], query
            assert body["top"]["key"] == "yettinchi"
            assert [group["type"] for group in body["groups"]] == ["problem"]

    def test_one_letter_is_still_not_a_query(self, numbered) -> None:
        assert find("t")["total"] == 0
        assert find("#")["total"] == 0

    def test_a_hidden_problem_is_not_found_by_its_number(self, db) -> None:
        Problem.objects.create(slug="yopiq", title="Yopiq", statement="x", difficulty=800, code=77)
        assert find("77")["counts"]["problem"] == 0

    def test_words_are_not_read_as_a_number(self) -> None:
        from problems.search import by_number

        assert by_number("graf") is None
        assert by_number("12a") is None
        assert by_number("9" * 12) is None  # not an integer the column can hold


@pytest.mark.django_db
class TestTopHit:
    """Robocontest answers «@ali» with that user on top; so do we."""

    def test_a_problem_number_is_the_top_hit(self, numbered) -> None:
        top = find("1519")["top"]
        assert top is not None
        assert (top["type"], top["key"]) == ("problem", "toliq-qism-graf")

    def test_an_exact_username_is_the_top_hit(self, user) -> None:
        User.objects.create_user(username="azizbek", password="Parol!12345")
        top = find("aziz", type="user")["top"]
        assert top is not None and top["key"] == "aziz"

    def test_a_partial_match_names_nothing(self, user) -> None:
        assert find("azi")["top"] is None

    def test_no_match_no_top(self, db) -> None:
        assert find("zzzzqq")["top"] is None

    def test_a_problem_number_beats_a_user_with_that_name(self, numbered) -> None:
        User.objects.create_user(username="1519", password="Parol!12345")
        top = find("1519")["top"]
        assert top is not None and top["type"] == "problem"


@pytest.mark.django_db
class TestInsideTheText:
    """Robocontest finds a blog post by a word in its body."""

    def test_a_word_in_the_body_finds_the_article(self, db) -> None:
        Article.objects.create(
            slug="bfs",
            title="Kenglik bo'yicha qidiruv",
            body="Kirish. Bu usul navbat (queue) tuzilmasiga tayanadi va qatlamma-qatlam yuradi.",
            is_published=True,
        )
        hit = hits(find("navbat"), "learn")[0]
        assert hit["key"] == "bfs"
        assert "navbat" in hit["snippet"]
        assert hit["snippet"].startswith("Kirish") or hit["snippet"].startswith("…")

    def test_a_title_match_ranks_above_a_body_match_and_carries_no_snippet(self, db) -> None:
        Post.objects.create(
            slug="matnda", title="Boshqa mavzu", body="Bu yerda reyting haqida.", is_published=True
        )
        Post.objects.create(slug="sarlavhada", title="Reyting tizimi", body="x", is_published=True)
        found = hits(find("reyting"), "news")
        assert [hit["key"] for hit in found] == ["sarlavhada", "matnda"]
        assert "snippet" not in found[0]
        assert "reyting" in found[1]["snippet"]

    def test_the_excerpt_is_cut_from_the_original_text(self) -> None:
        text = "Avval " + "so'z " * 30 + "yig'indini hisoblang, keyin " + "davom " * 30
        quoted = site_search.excerpt(text, "yigindini")
        assert "yig'indini" in quoted  # the apostrophe the fold dropped is back
        assert quoted.startswith("…") and quoted.endswith("…")
        assert len(quoted) < 160

    def test_no_excerpt_when_the_text_does_not_hold_the_needle(self) -> None:
        assert site_search.excerpt("Boshqa narsa", "graf") == ""


@pytest.mark.django_db
class TestNewSources:
    def test_shop_items(self, db) -> None:
        ShopItem.objects.create(
            code="oltin-ramka",
            category=ShopItem.Category.AVATAR_FRAME,
            title_uz="Oltin ramka",
            title_en="Golden frame",
            price=120,
        )
        ShopItem.objects.create(
            code="eski",
            category=ShopItem.Category.AVATAR_FRAME,
            title_uz="Eski ramka",
            price=10,
            is_active=False,
        )
        assert keys(find("ramka"), "shop") == ["oltin-ramka"]
        assert keys(find("golden"), "shop") == ["oltin-ramka"]
        assert hits(find("ramka"), "shop")[0]["meta"] == 120

    def test_the_product_roadmap(self, db) -> None:
        item = RoadmapItem.objects.create(title="Jamoaviy musobaqalar", body="ICPC uslubida")
        found = {hit["kind"]: hit["key"] for hit in hits(find("jamoaviy"), "news")}
        assert found == {"plan": str(item.pk)}

    def test_a_change_is_found_by_its_translated_title(self, db) -> None:
        update = SystemUpdate.objects.create(
            title="Qidiruv yangilandi",
            kind=SystemUpdate.Kind.IMPROVED,
            module=SystemUpdate.Module.CORE,
            status=SystemUpdate.Status.PUBLISHED,
            released_at=timezone.now().date(),
        )
        # Latin on purpose: SQLite's LOWER (local tests) is ASCII-only.
        SystemUpdateTranslation.objects.create(update=update, locale="en", title="Search renewed")
        hit = hits(find("renewed"), "news")[0]
        assert (hit["kind"], hit["key"]) == ("update_translation", str(update.pk))

    def test_a_translation_of_a_draft_stays_out(self, db) -> None:
        update = SystemUpdate.objects.create(
            title="Qoralama",
            kind=SystemUpdate.Kind.NEW,
            module=SystemUpdate.Module.CORE,
            released_at=timezone.now().date(),
        )
        SystemUpdateTranslation.objects.create(update=update, locale="en", title="Secret draft")
        assert find("secret")["total"] == 0


@pytest.mark.django_db
class TestLargeTableGuard:
    """`%%` and `__` took 273 ms on the live user table (2026-10-06)."""

    def test_punctuation_alone_does_not_ask_the_user_table(
        self, user, django_assert_max_num_queries
    ) -> None:
        User.objects.create_user(username="__under__", password="Parol!12345")
        source = site_search.sources("user")[0]
        assert not site_search._askable(source, "__")
        assert not site_search._askable(source, "%%")
        assert site_search._askable(source, "az")
        assert find("__")["counts"]["user"] == 0

    def test_a_name_with_punctuation_is_still_found_by_its_letters(self, db) -> None:
        User.objects.create_user(username="__under__", password="Parol!12345")
        assert keys(find("__un"), "user") == ["__under__"]

    def test_small_sources_are_always_asked(self) -> None:
        source = site_search.sources("topic")[0]
        assert site_search._askable(source, "%%")


@pytest.mark.django_db
class TestThrottle:
    """Forty requests in a row all answered 200 before this."""

    @pytest.fixture(autouse=True)
    def tight(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            SearchRateThrottle, "THROTTLE_RATES", {"search": "3/min"}, raising=False
        )

    def test_the_search_has_its_own_limit(self) -> None:
        client = APIClient()
        codes = [client.get(reverse("search"), {"q": f"graf{n}"}).status_code for n in range(5)]
        assert codes == [200, 200, 200, 429, 429]

    def test_the_refusal_says_when_to_come_back(self) -> None:
        client = APIClient()
        for n in range(3):
            client.get(reverse("search"), {"q": f"graf{n}"})
        response = client.get(reverse("search"), {"q": "graf"})
        assert response.status_code == 429
        assert int(response["Retry-After"]) > 0

    def test_other_endpoints_do_not_share_the_bucket(self) -> None:
        client = APIClient()
        for n in range(4):
            client.get(reverse("search"), {"q": f"graf{n}"})
        assert client.get(reverse("problem-list")).status_code == 200

    def test_a_server_side_render_is_not_counted_here(self, settings) -> None:
        """`/search` renders on the server and calls from a private address
        with no client header — all visitors would share one bucket."""
        settings.TRUSTED_CLIENT_IP_HEADER = "HTTP_CF_CONNECTING_IP"
        client = APIClient(REMOTE_ADDR="172.18.0.5")
        codes = {client.get(reverse("search"), {"q": f"graf{n}"}).status_code for n in range(6)}
        assert codes == {200}

    def test_a_visitor_behind_the_proxy_is_counted_by_their_own_address(self, settings) -> None:
        settings.TRUSTED_CLIENT_IP_HEADER = "HTTP_CF_CONNECTING_IP"
        first = APIClient(REMOTE_ADDR="172.18.0.5", HTTP_CF_CONNECTING_IP="203.0.113.7")
        second = APIClient(REMOTE_ADDR="172.18.0.5", HTTP_CF_CONNECTING_IP="203.0.113.8")
        for n in range(3):
            first.get(reverse("search"), {"q": f"graf{n}"})
        assert first.get(reverse("search"), {"q": "graf"}).status_code == 429
        assert second.get(reverse("search"), {"q": "graf"}).status_code == 200
