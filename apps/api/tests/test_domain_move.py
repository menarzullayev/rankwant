"""Domen almashishi — eski manzildagi avatarlar (rankwant.bugvector.uz → rankwant.uz)."""

from __future__ import annotations

import io
from typing import Any

import pytest
from django.core.management import call_command

from core import avatars
from core.models import User

NAME = "abcdefghijklmnopqrstuvwx.png"
OLD = "https://rankwant.bugvector.uz"


def test_eski_domendagi_avatar_ham_taniladi(settings: Any) -> None:
    settings.SITE_URL = "https://rankwant.uz"
    settings.ALLOWED_HOSTS = ["rankwant.uz", "rankwant.bugvector.uz"]

    assert avatars.name_from_url(f"https://rankwant.uz/api/v1/avatars/{NAME}") == NAME
    assert avatars.name_from_url(f"{OLD}/api/v1/avatars/{NAME}") == NAME
    assert avatars.name_from_url(f"https://begona.example/api/v1/avatars/{NAME}") is None
    assert avatars.name_from_url(f"https://rankwant.uz/boshqa/{NAME}") is None


@pytest.mark.django_db
def test_avatar_manzillari_kochiriladi(user: User, other_user: User, settings: Any) -> None:
    settings.SITE_URL = "https://rankwant.uz"
    user.avatar_url = f"{OLD}/api/v1/avatars/{NAME}"
    user.save(update_fields=["avatar_url"])
    other_user.avatar_url = "https://cdn.example/rasm.png"
    other_user.save(update_fields=["avatar_url"])

    call_command("rehost_avatars", OLD, stdout=io.StringIO())
    call_command("rehost_avatars", OLD, stdout=io.StringIO())

    user.refresh_from_db()
    other_user.refresh_from_db()
    assert user.avatar_url == f"https://rankwant.uz/api/v1/avatars/{NAME}"
    assert other_user.avatar_url == "https://cdn.example/rasm.png"
