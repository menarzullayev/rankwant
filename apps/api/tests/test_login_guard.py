"""Failed sign-ins are limited per address and per account (2026-10-05)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core import login_guard
from core.models import User

PASSWORD = "Parol!12345"


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def rates(settings):
    """Small limits, so a test does not need twenty requests."""

    def use(ip: str, account: str) -> None:
        settings.REST_FRAMEWORK = {
            **settings.REST_FRAMEWORK,
            "DEFAULT_THROTTLE_RATES": {
                **settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"],
                "login_ip": ip,
                "login_account": account,
            },
        }

    return use


def sign_in(client: APIClient, identifier: str, password: str, address: str = "10.0.0.1"):
    return client.post(
        reverse("login"),
        {"identifier": identifier, "password": password},
        format="json",
        REMOTE_ADDR=address,
    )


@pytest.mark.django_db
class TestLoginGuard:
    def test_account_bucket_stops_the_right_password_too(self, client, user, rates) -> None:
        rates("100/hour", "3/hour")
        for _ in range(3):
            assert sign_in(client, "aziz", "wrong").status_code == 401

        r = sign_in(client, "aziz", PASSWORD)

        assert r.status_code == 429, r.content
        assert int(r["Retry-After"]) > 0
        # The limit is on the name, whatever the address.
        assert sign_in(client, "aziz", PASSWORD, address="10.0.0.99").status_code == 429

    def test_another_account_is_not_affected(self, client, user, other_user, rates) -> None:
        rates("100/hour", "3/hour")
        for _ in range(3):
            sign_in(client, "aziz", "wrong")

        assert sign_in(client, "bekzod", PASSWORD).status_code == 200

    def test_address_bucket_stops_a_sweep_over_many_accounts(self, client, user, rates) -> None:
        rates("3/hour", "100/hour")
        for name in ("a1", "a2", "a3"):
            assert sign_in(client, name, "wrong").status_code == 401

        assert sign_in(client, "aziz", PASSWORD).status_code == 429
        # Another address still signs in.
        assert sign_in(client, "aziz", PASSWORD, address="10.0.0.2").status_code == 200

    def test_successful_sign_ins_are_not_counted(self, client, user, rates) -> None:
        """A classroom behind one address signs in many times; that is not guessing."""
        rates("3/hour", "3/hour")
        for _ in range(6):
            assert sign_in(APIClient(), "aziz", PASSWORD).status_code == 200

    def test_name_is_compared_without_case_or_spaces(self, client, user, rates) -> None:
        rates("100/hour", "3/hour")
        for typed in ("AZIZ", " aziz ", "Aziz"):
            sign_in(client, typed, "wrong")

        assert sign_in(client, "aziz", PASSWORD).status_code == 429

    def test_unknown_name_is_limited_like_a_real_one(self, client, db, rates) -> None:
        """The bucket must not tell whether the account exists (ADR-0015)."""
        rates("100/hour", "3/hour")
        for _ in range(3):
            assert sign_in(client, "nobody", "wrong").status_code == 401
        assert not User.objects.filter(username="nobody").exists()

        assert sign_in(client, "nobody", "wrong").status_code == 429

    def test_a_broken_guard_does_not_refuse_sign_ins(
        self, client, user, rates, monkeypatch
    ) -> None:
        """The guard is not allowed to become a second way for sign-in to fail."""
        rates("3/hour", "3/hour")

        def broken(*args, **kwargs):
            raise ConnectionError("cache down")

        monkeypatch.setattr(login_guard, "_buckets", broken)

        assert sign_in(client, "aziz", "wrong").status_code == 401
        assert sign_in(client, "aziz", PASSWORD).status_code == 200

    def test_an_empty_rate_switches_a_bucket_off(self, client, user, rates) -> None:
        rates("", "")
        for _ in range(12):
            sign_in(client, "aziz", "wrong")

        assert sign_in(client, "aziz", PASSWORD).status_code == 200
