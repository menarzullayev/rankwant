"""Standings by region (decision 2026-11-10 ②, contests.regional)."""

from __future__ import annotations

from typing import Any

import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from contests.models import Contest, Standing
from contests.regional import cache_key, cache_keys
from contests.services import rebuild_standings
from core.models import User

pytestmark = pytest.mark.django_db


def _row(contest: Contest, username: str, position: int, rank: int, **user: Any) -> User:
    person = User.objects.create_user(username=username, password="Parol!12345", **user)
    Standing.objects.create(contest=contest, user=person, position=position, rank=rank)
    return person


@pytest.fixture
def table(contest: Contest) -> Contest:
    capital = {"country": "UZ", "region": "toshkent-shahri"}
    _row(contest, "birinchi", 1, 1, **capital)
    _row(contest, "samarqandlik", 2, 2, country="UZ", region="samarqand")
    # Hid their location: no regional view may find them.
    _row(contest, "yashirin", 3, 3, hidden_fields=["email", "country"], **capital)
    tester = _row(contest, "sinovchi", 4, 0, **capital)
    Standing.objects.filter(user=tester).update(insider_role=Standing.InsiderRole.TESTER)
    _row(contest, "uchinchi", 5, 4, **capital)
    _row(contest, "chetdan", 6, 5, country="KZ", region="toshkent-shahri")
    return contest


def _standings(contest: Contest, **query: str) -> dict[str, Any]:
    response = APIClient().get(reverse("contest-standings", args=[contest.slug]), query)
    assert response.status_code == 200, response.content
    body: dict[str, Any] = response.json()
    return body


def test_region_keeps_its_rows_in_order_with_their_own_places(table: Contest) -> None:
    body = _standings(table, region="toshkent-shahri")
    assert body["region"] == "toshkent-shahri"
    rows = [(r["username"], r["rank"], r["region_rank"]) for r in body["results"]]
    # The tester sits in the table with no place; the hidden one and the
    # Kazakh `toshkent-shahri` (free text abroad) are not there.
    assert rows == [("birinchi", 1, 1), ("sinovchi", 0, 0), ("uchinchi", 4, 2)]


def test_regions_offer_only_public_locations(table: Contest) -> None:
    body = _standings(table)
    assert body["regions"] == [
        {"code": "toshkent-shahri", "count": 3},
        {"code": "samarqand", "count": 1},
    ]
    assert body["region"] == ""
    assert all(row["region_rank"] is None for row in body["results"])
    assert len(body["results"]) == 6


def test_unknown_region_is_refused(table: Contest) -> None:
    response = APIClient().get(
        reverse("contest-standings", args=[table.slug]), {"region": "moskva"}
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_region"


def test_rebuild_clears_every_regional_table(contest: Contest) -> None:
    assert cache_key(contest.pk, "samarqand") in cache_keys(contest.pk)
    for key in cache_keys(contest.pk):
        cache.set(key, {"stale": True}, 60)
    rebuild_standings(contest)
    assert all(cache.get(key) is None for key in cache_keys(contest.pk))
