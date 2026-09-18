"""Account deletion covers every personal field of `User`.

`core.account` lists each field as cleared or kept. These tests fail when a new
field is in neither list, when `anonymize` leaves a cleared field as it was, or
when `export` leaves one out. `phone` slipped through all three until
2026-09-18 (ADR-0024).
"""

from __future__ import annotations

from datetime import date

import pytest
from django.utils import timezone

from core import account
from core.models import School, User


def concrete_fields() -> set[str]:
    return {
        field.name
        for field in User._meta.get_fields()
        if getattr(field, "concrete", False) or (field.many_to_many and not field.auto_created)
    }


def test_every_field_is_classified() -> None:
    cleared, kept = set(account.CLEARED_FIELDS), set(account.KEPT_FIELDS)

    assert not cleared & kept, f"in both lists: {sorted(cleared & kept)}"
    assert concrete_fields() - cleared - kept == set(), "classify the new field in core/account.py"
    assert (cleared | kept) - concrete_fields() == set(), "listed but not a User field"


@pytest.mark.django_db
def test_anonymize_clears_every_personal_field() -> None:
    school = School.objects.create(name="1-maktab")
    now = timezone.now()
    user = User.objects.create_user(
        username="ochiriladi",
        password="Parol!12345",
        email="ochiriladi@rankwant.uz",
        display_name="Ochiriladi",
        first_name="Ali",
        last_name="Valiyev",
        email_verified_at=now,
        avatar_url="https://rankwant.uz/avatar.png",
        bio="bio",
        telegram_id=123,
        country="UZ",
        region="toshkent-sh",
        district="yunusobod",
        city="Toshkent",
        school="1-maktab",
        school_ref=school,
        grade="9",
        website="https://example.org",
        birth_date=date(2010, 1, 1),
        phone="+998901234567",
        hidden_fields=["email", "country"],
        pinned_achievements=["solved_1"],
        ui_prefs={"version": 2},
        notify_prefs={"contest_result": {"site": True}},
        marketing_opt_in=True,
        shirt_size="M",
        postal_recipient="Ali Valiyev",
        postal_country="UZ",
        postal_region="Toshkent",
        postal_city="Toshkent",
        postal_address="Amir Temur 1",
        postal_code="100000",
        coach_can_view_attempts=True,
        message_min_rating=1500,
        device_fingerprint="ab" * 32,
        duel_ready_until=now,
        last_seen_at=now,
    )
    before = {name: getattr(user, name) for name in account.CLEARED_FIELDS}

    account.anonymize(user)

    user.refresh_from_db()
    kept_as_was = [name for name in account.CLEARED_FIELDS if getattr(user, name) == before[name]]
    assert kept_as_was == [], f"anonymize left these as they were: {kept_as_was}"


@pytest.mark.django_db
def test_export_returns_every_personal_field(user: User) -> None:
    profile = account.export(user)["profile"]

    # The password hash, the active flag and the derived skeleton are not data
    # the person gave us.
    missing = (
        set(account.CLEARED_FIELDS)
        - set(profile)
        - {
            "password",
            "is_active",
            "username_skeleton",
        }
    )
    assert missing == set(), f"export leaves out: {sorted(missing)}"
