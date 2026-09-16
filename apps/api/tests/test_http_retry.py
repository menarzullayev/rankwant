"""core.http_retry — 429/5xx qayta urinishi.

Tarmoqqa chiqilmaydi: `urllib.request.urlopen` o'rniga hisoblagich
qo'yiladi, `time.sleep` yozib boriladi, `random.uniform` esa 0 ga
mahkamlanadi (jitter natijani oldindan aytib bo'lmaydigan qilardi).
"""

from __future__ import annotations

import email.message
import io
import random
import time
import urllib.error
import urllib.request
from typing import Any

import pytest

from core import http_retry
from core.http_retry import MAX_RETRY_AFTER, RETRIES, open_with_retry


class _Recorder:
    """Ketma-ket javoblar: istisno yoki tanani navbat bo'yicha qaytaradi."""

    def __init__(self, *responses: Any) -> None:
        self.responses = list(responses)
        self.calls = 0

    def __call__(self, request: Any, timeout: float | None = None) -> Any:
        self.calls += 1
        # Oxirgi javob qayta-qayta ishlatiladi: navbat tugasa ham chaqiruv
        # javobsiz qolmasin (`test_gives_up_after_all_attempts` shunga
        # tayanadi).
        index = min(self.calls - 1, len(self.responses) - 1)
        item = self.responses[index]
        if isinstance(item, Exception):
            raise item
        return io.BytesIO(item)


def _http_error(code: int, headers: dict[str, str] | None = None) -> urllib.error.HTTPError:
    message = email.message.Message()
    for key, value in (headers or {}).items():
        message[key] = value
    return urllib.error.HTTPError("https://example.test/x", code, "x", message, io.BytesIO(b""))


@pytest.fixture
def waits(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """`sleep` qiymatlarini yig'adi, jitter'ni o'chiradi."""
    recorded: list[float] = []
    monkeypatch.setattr(time, "sleep", recorded.append)
    monkeypatch.setattr(random, "uniform", lambda _a, _b: 0.0)
    return recorded


def _patch(monkeypatch: pytest.MonkeyPatch, recorder: _Recorder) -> None:
    monkeypatch.setattr(urllib.request, "urlopen", recorder)


def test_retries_on_429_then_succeeds(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    recorder = _Recorder(_http_error(429), _http_error(429), b"ok")
    _patch(monkeypatch, recorder)

    with open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1) as resp:
        assert resp.read() == b"ok"

    assert recorder.calls == 3
    assert len(waits) == 2


def test_honours_retry_after_header(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    recorder = _Recorder(_http_error(429, {"Retry-After": "7"}), b"ok")
    _patch(monkeypatch, recorder)

    with open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1):
        pass

    assert waits == [7.0]


def test_retry_after_is_capped(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    """Provayder 1 soat kut desa, navbat qotib qolmasin."""
    recorder = _Recorder(_http_error(429, {"Retry-After": "3600"}), b"ok")
    _patch(monkeypatch, recorder)

    with open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1):
        pass

    assert waits == [MAX_RETRY_AFTER]


def test_no_retry_on_404(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    """4xx — bizning so'rov xatosi; qayta urinish uni to'g'rilamaydi."""
    recorder = _Recorder(_http_error(404))
    _patch(monkeypatch, recorder)

    with pytest.raises(urllib.error.HTTPError):
        open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1)

    assert recorder.calls == 1
    assert waits == []


def test_gives_up_after_all_attempts(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    recorder = _Recorder(_http_error(429))
    _patch(monkeypatch, recorder)

    with pytest.raises(urllib.error.HTTPError):
        open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1)

    assert recorder.calls == RETRIES + 1
    assert len(waits) == RETRIES


def test_network_error_retries_with_growing_backoff(
    monkeypatch: pytest.MonkeyPatch, waits: list[float]
) -> None:
    recorder = _Recorder(urllib.error.URLError("dns"), urllib.error.URLError("dns"), b"ok")
    _patch(monkeypatch, recorder)

    with open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1):
        pass

    assert waits == [http_retry.BACKOFF, http_retry.BACKOFF * 2]


def test_backoff_is_capped(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    """Eksponensial o'sish cheksiz emas — navbat soatlab uxlab qolmasin."""
    recorder = _Recorder(*[urllib.error.URLError("x")] * 5, b"ok")
    _patch(monkeypatch, recorder)

    with open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1, retries=5):
        pass

    assert waits == [0.5, 1.0, 2.0, 4.0, http_retry.MAX_BACKOFF]
    assert max(waits) == http_retry.MAX_BACKOFF


def test_retry_after_http_date(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    """Ba'zi provayderlar soniya emas, sana yuboradi."""
    recorder = _Recorder(_http_error(429, {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}), b"ok")
    _patch(monkeypatch, recorder)

    with open_with_retry(urllib.request.Request("https://example.test/x"), timeout=1):
        pass

    assert waits == [MAX_RETRY_AFTER]


def test_custom_opener_is_used(monkeypatch: pytest.MonkeyPatch, waits: list[float]) -> None:
    """Yo'naltirishni o'chirgan opener (`core.avatars`) ham ishlashi shart."""
    recorder = _Recorder(_http_error(503), b"ok")

    class _Opener:
        def open(self, request: Any, timeout: float | None = None) -> Any:
            return recorder(request, timeout)

    with open_with_retry(
        urllib.request.Request("https://example.test/x"),
        timeout=1,
        opener=_Opener(),  # type: ignore[arg-type]
    ):
        pass

    assert recorder.calls == 2
