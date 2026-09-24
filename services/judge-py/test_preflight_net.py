"""check_network testlari — ADR-0028 fail-closed kontrakti (judge-py tomoni).

Testlar HAQIQIY socketlar bilan ishlaydi: ochiq listener = «ulanish
muvaffaqiyatli» = PreflightError; yopiq port = refused — o'tadi;
mavjud bo'lmagan DNS nomi = yechilmadi — o'tadi.
"""

from __future__ import annotations

import socket
from collections.abc import Iterator

import pytest

import preflight


@pytest.fixture
def open_listener() -> Iterator[tuple[str, int]]:
    """Ochiq (qabul qiluvchi) TCP port — ulanish MUVAFFAQIYATLI bo'lishi kerak."""
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(4)
    try:
        yield srv.getsockname()[:2]
    finally:
        srv.close()


@pytest.fixture
def closed_port() -> int:
    """Erkin port (listener yo'q) — ulanish refused bo'lishi kutiladi."""
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    port = srv.getsockname()[1]
    srv.close()
    return port


def _run(
    monkeypatch: pytest.MonkeyPatch, postgres_host: str, postgres_port: int, forbidden: str
) -> None:
    monkeypatch.setenv("JUDGE_NET_PREFLIGHT", "1")
    monkeypatch.setenv("POSTGRES_HOST", postgres_host)
    monkeypatch.setenv("POSTGRES_PORT", str(postgres_port))
    monkeypatch.setenv("JUDGE_FORBIDDEN_HOSTS", forbidden)


def test_open_target_fails(monkeypatch: pytest.MonkeyPatch, open_listener: tuple[str, int]) -> None:
    host, port = open_listener
    with pytest.raises(preflight.PreflightError, match="MUVAFFAQIYATLI"):
        _run(monkeypatch, host, port, f"{host}:{port}")
        preflight.check_network()


def test_refused_passes(monkeypatch: pytest.MonkeyPatch, closed_port: int) -> None:
    # ⚠️ host nomi EMAS: testlar hostda yuradi, «api» nomi bu yerda DNS'da
    # yo'q — yechilmagan nom «yopiq» bo'ladi va test yolg'on o'tardi.
    _run(monkeypatch, "127.0.0.1", closed_port, f"127.0.0.1:{closed_port}")
    preflight.check_network()  # xato yo'q


def test_unresolved_dns_passes(monkeypatch: pytest.MonkeyPatch, closed_port: int) -> None:
    _run(monkeypatch, "preflight-net-test.invalid", 5432, f"127.0.0.1:{closed_port}")
    preflight.check_network()  # xato yo'q


def test_forbidden_open_target_fails_even_if_postgres_closed(
    monkeypatch: pytest.MonkeyPatch, closed_port: int, open_listener: tuple[str, int]
) -> None:
    open_host, open_port = open_listener
    with pytest.raises(preflight.PreflightError):
        _run(monkeypatch, "127.0.0.1", closed_port, f"{open_host}:{open_port}")
        preflight.check_network()


def test_malformed_entry_fails_closed(monkeypatch: pytest.MonkeyPatch, closed_port: int) -> None:
    _run(monkeypatch, "127.0.0.1", closed_port, "api-port-isiz")
    with pytest.raises(preflight.PreflightError, match="port bo'lmagan"):
        preflight.check_network()


def test_out_of_range_port_fails_closed(monkeypatch: pytest.MonkeyPatch, closed_port: int) -> None:
    _run(monkeypatch, "127.0.0.1", closed_port, "api:99999")
    with pytest.raises(preflight.PreflightError, match="noto'g'ri port"):
        preflight.check_network()


def test_gate_off_skips_everything(
    monkeypatch: pytest.MonkeyPatch, open_listener: tuple[str, int]
) -> None:
    """JUDGE_NET_PREFLIGHT != 1 → hech narsa tekshirilmaydi (compose gate)."""
    host, port = open_listener
    monkeypatch.delenv("JUDGE_NET_PREFLIGHT", raising=False)
    monkeypatch.setenv("POSTGRES_HOST", host)
    monkeypatch.setenv("POSTGRES_PORT", str(port))
    monkeypatch.setenv("JUDGE_FORBIDDEN_HOSTS", f"api:{port}")
    preflight.check_network()  # ochiq manzil baribir — o'tdi (gate off)
