"""Turnstile tekshiruvi — 9-qaror.

Asosiy shart: KALITLAR YO'Q BO'LSA tekshiruv butunlay o'chadi. Bu
ataylab — `test` muhiti tarmoqqa chiqmasligi kerak, ya'ni hech bir
birlik testida Cloudflare'ga so'rov ketmaydi.

Ikkinchi shart: Cloudflare javob bermasa ro'yxatdan o'tish TO'XTAMAYDI
(`TURNSTILE_FAIL_OPEN`). Turnstile — qo'shimcha qavat, yagona himoya
emas: throttle allaqachon ishlaydi.
"""

from __future__ import annotations

import json
from typing import Any
from unittest import mock

import pytest

from core import turnstile


class Javob:
    """`urlopen` o'rniga — ko'rsatilgan JSON ni qaytaradi."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = json.dumps(data).encode()

    def read(self) -> bytes:
        return self._data

    def __enter__(self) -> Javob:
        return self

    def __exit__(self, *_: Any) -> None:
        return None


@pytest.fixture
def kalitlar(settings: Any) -> None:
    settings.TURNSTILE_SITE_KEY = "sayt"
    settings.TURNSTILE_SECRET_KEY = "sir"
    settings.TURNSTILE_FAIL_OPEN = True


class TestOchirilgan:
    def test_kalitsiz_otkazib_yuboriladi(self, settings: Any) -> None:
        """Kalitlar bo'sh — tekshiruv o'chiq, ya'ni `verify` jim o'tadi."""
        settings.TURNSTILE_SITE_KEY = ""
        settings.TURNSTILE_SECRET_KEY = ""

        assert turnstile.enabled() is False
        turnstile.verify("")

    def test_chala_sozlama_ochiq_ochiradi(self, settings: Any) -> None:
        """Faqat sayt kaliti bo'lsa `enabled()` `True` bo'lmasligi kerak.

        Aks holda har urinish yiqilardi: yashirin kalit yo'q, ya'ni
        Cloudflare'ga yuboriladigan hech narsa yo'q.
        """
        settings.TURNSTILE_SITE_KEY = "sayt"
        settings.TURNSTILE_SECRET_KEY = ""

        assert turnstile.enabled() is False
        turnstile.verify("")


class TestTekshiruv:
    def test_token_yoq_rad_etiladi(self, kalitlar: None) -> None:
        with pytest.raises(turnstile.TurnstileError):
            turnstile.verify("")

    def test_muvaffaqiyat(self, kalitlar: None) -> None:
        with mock.patch("urllib.request.urlopen", return_value=Javob({"success": True})):
            turnstile.verify("tok", remote_ip="1.2.3.4")

    def test_rad_etish(self, kalitlar: None) -> None:
        with mock.patch("urllib.request.urlopen", return_value=Javob({"success": False})):
            with pytest.raises(turnstile.TurnstileError):
                turnstile.verify("tok")

    def test_tarmoq_xatosi_otkazib_yuboradi(self, kalitlar: None) -> None:
        with mock.patch("urllib.request.urlopen", side_effect=OSError("tarmoq yo'q")):
            turnstile.verify("tok")

    def test_tarmoq_xatosi_yopiq_siyosatda_rad_etadi(self, kalitlar: None, settings: Any) -> None:
        settings.TURNSTILE_FAIL_OPEN = False

        with mock.patch("urllib.request.urlopen", side_effect=OSError("tarmoq yo'q")):
            with pytest.raises(turnstile.TurnstileError):
                turnstile.verify("tok")
