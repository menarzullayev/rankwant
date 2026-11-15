"""The public leaderboard hides the accounts the smoke and latency checks register.

Found 2026-11-15 on the live home page: three of the five leaders were `smoke…` accounts
created by the nightly smoke test (800 points each, the starting value), next to the
founder. Profiles stay reachable by name; only the list is filtered.
"""

from __future__ import annotations

import re

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from core.views import AUTOMATED_USERNAME

AUTOMATED = ["smoke1790231924", "latency179223695187771e", "smokeabcdef12", "latency00000000"]
#: Real handles that merely start the same way.
REAL = ["smoke11", "smoke112", "smoker", "smoke_fan", "latency", "smoke1234567", "Smoke1790231924x"]


def _usernames(client: APIClient) -> list[str]:
    response = client.get(reverse("user-list"), {"page_size": 100})
    assert response.status_code == 200
    return [row["username"] for row in response.json()["results"]]


@pytest.mark.django_db
class TestLeaderboardHidesAutomatedAccounts:
    def test_automated_accounts_are_not_listed(self) -> None:
        for name in AUTOMATED:
            User.objects.create_user(username=name, password="x", rating_skills=800)
        User.objects.create_user(username="ali", password="x", rating_skills=900)

        listed = _usernames(APIClient())

        assert "ali" in listed
        assert not set(AUTOMATED) & set(listed)

    @pytest.mark.parametrize("name", REAL)
    def test_real_handles_with_a_similar_start_stay_listed(self, name: str) -> None:
        User.objects.create_user(username=name, password="x", rating_skills=800)
        assert name in _usernames(APIClient())

    def test_demo_origin_accounts_are_not_listed_but_imported_ones_are(self) -> None:
        User.objects.create_user(username="seeded", password="x", origin=User.Origin.DEMO)
        # A real person's handle that merely says "demo" (it exists on the live site).
        User.objects.create_user(username="demo", password="x", origin=User.Origin.IMPORTED)

        listed = _usernames(APIClient())

        assert "seeded" not in listed
        assert "demo" in listed

    def test_an_automated_profile_is_still_reachable_by_name(self) -> None:
        User.objects.create_user(username="smoke1790231924", password="x")
        response = APIClient().get(reverse("user-detail", args=["smoke1790231924"]))
        assert response.status_code == 200

    def test_the_pattern_matches_what_the_checks_register(self) -> None:
        pattern = re.compile(AUTOMATED_USERNAME)
        assert all(pattern.match(name) for name in AUTOMATED)
        assert not any(pattern.match(name) for name in REAL)
