"""`User.grade` takes a code from `profiles.catalog.GRADES` (ADR-0024)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from profiles.catalog import GRADES

# ⚠️ Yo'l `packages/shared/src/grades.ts` (2026-09-24). Monorepo
# restrukturizatsiyasidan keyin ro'yxat `apps/web/src/lib/` dan
# `@rankwant/shared` paketiga ko'chdi; eski yo'l `FileNotFoundError`
# berardi va Nightly'ning API coverage job'i shu sabab yiqilardi.
WEB_GRADES = Path(__file__).resolve().parents[3] / "packages/shared/src/grades.ts"


def kirgan(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def patch(user: User, body: dict[str, str]) -> int:
    return int(kirgan(user).patch(reverse("me"), body, format="json").status_code)


@pytest.mark.django_db
class TestGradeCodes:
    @pytest.mark.parametrize("code", ["1", "11", "b4", "m2", "teacher", "other", ""])
    def test_codes_are_accepted(self, user: User, code: str) -> None:
        assert patch(user, {"grade": code}) == 200
        user.refresh_from_db()
        assert user.grade == code

    @pytest.mark.parametrize("value", ["9-sinf", "12", "m3", "Teacher"])
    def test_free_text_is_rejected(self, user: User, value: str) -> None:
        assert patch(user, {"grade": value}) == 400

    def test_a_value_saved_before_the_catalogue_survives_other_edits(self, user: User) -> None:
        User.objects.filter(pk=user.pk).update(grade="9-A")
        user.refresh_from_db()

        # The settings form sends every field, the untouched grade included.
        assert patch(user, {"grade": "9-A", "bio": "salom"}) == 200
        assert patch(user, {"grade": "9-B"}) == 400


def test_web_list_matches_the_api() -> None:
    source = WEB_GRADES.read_text(encoding="utf-8")
    block = re.search(r"GRADE_CODES = \[(.*?)\] as const", source, re.S)
    assert block, f"{WEB_GRADES}: GRADE_CODES not found"
    assert tuple(re.findall(r'"([^"]+)"', block.group(1))) == GRADES
