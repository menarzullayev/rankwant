"""50k: Redis providers + standings — origin takror COUNT/JOIN qilmasin."""

from __future__ import annotations

from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient


def test_providers_bir_marta_hisoblanadi(monkeypatch, db) -> None:
    from core import oauth
    from core.views import AuthProvidersView

    cache.delete(AuthProvidersView.CACHE_KEY)
    calls = {"n": 0}
    inner = oauth.configured

    def once() -> list[str]:
        calls["n"] += 1
        return inner()

    monkeypatch.setattr(oauth, "configured", once)
    APIClient().get(reverse("auth-providers"))
    APIClient().get(reverse("auth-providers"))
    assert calls["n"] == 1


def test_standings_keshdan_qaytadi(contest, monkeypatch) -> None:
    cached = {"frozen": False, "results": [{"rank": 1, "username": "kesh"}]}
    monkeypatch.setattr("contests.views.cache_get", lambda key: cached)
    body = APIClient().get(reverse("contest-standings", args=[contest.slug])).json()
    assert body["results"][0]["username"] == "kesh"


def test_standings_yozuv_keshni_ochadi(contest) -> None:
    from contests.services import STANDINGS_CACHE_KEY, _write

    key = STANDINGS_CACHE_KEY.format(contest_id=contest.pk)
    cache.set(key, {"stale": True}, 60)
    _write(contest, [], score=lambda row: 0)
    assert cache.get(key) is None


def test_arena_standings_keshdan(db, monkeypatch) -> None:
    from tests.test_arena import _round

    arena = _round(-5)
    cached = {"results": [{"rank": 1, "username": "kesh"}]}
    monkeypatch.setattr("arena.views.cache_get", lambda key: cached)
    body = APIClient().get(reverse("arena-standings", args=[arena.slug])).json()
    assert body["results"][0]["username"] == "kesh"


def test_cache_delete_yengil() -> None:
    from core.cache import cache_delete, cache_get, cache_set

    cache_set("scale-50k-probe", 1, 60)
    assert cache_get("scale-50k-probe") == 1
    cache_delete("scale-50k-probe")
    assert cache_get("scale-50k-probe") is None


def test_kesh_yengil_fail_open(monkeypatch) -> None:
    from core.cache import cache_delete, cache_get, cache_set

    def boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("down")

    monkeypatch.setattr(cache, "get", boom)
    monkeypatch.setattr(cache, "set", boom)
    monkeypatch.setattr(cache, "delete", boom)
    assert cache_get("x", default="yoq") == "yoq"
    cache_set("x", 1)
    cache_delete("x")
