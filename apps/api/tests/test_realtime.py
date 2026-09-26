"""`realtime` — hodisa avtobusi va replay mantiqi (ADR-0029).

⚠️ Nega bu testlar muhim: replay mantiqi **jimgina** buziladigan sinf.
U noto'g'ri ishlasa oqim ochiladi, hodisalar keladi, sahifa yangilanadi —
va faqat ba'zi foydalanuvchilarda ba'zi o'zgarishlar ko'rinmay qoladi.
Bunday nosozlikni brauzerda ham, logda ham sezish qiyin.

Shu sababli bu yerda Redis **soxta**: mantiq (filtrlash, tartib, uzilish
aniqlash) haqiqiy Redis'siz ham tekshiriladi, CI esa tashqi xizmatsiz
ishlaydi.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from realtime import bus


class FakeRedis:
    """Faqat `replay_after` ishlatadigan ikki metod."""

    def __init__(self, entries: list[str]) -> None:
        self.entries = entries

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        return self.entries


def entry(seq: int, event: str = "verdict") -> str:
    return json.dumps({"id": seq, "event": event, "data": {"attempt_id": seq}})


@pytest.mark.django_db
class TestReplay:
    def test_songgi_id_dan_keyingilarini_qaytaradi(self) -> None:
        client = FakeRedis([entry(5), entry(4), entry(3)])
        events, gap = _run(client, last_id=3)
        assert [e["id"] for e in events] == [4, 5]
        assert gap is False

    def test_tartib_oshib(self) -> None:
        """Redis ro'yxati `LPUSH` bilan teskari yoziladi — tartib tuzatiladi."""
        client = FakeRedis([entry(9), entry(8), entry(7)])
        events, _ = _run(client, last_id=0)
        assert [e["id"] for e in events] == [7, 8, 9]

    def test_bufer_siqib_chiqargan_bolsa_uzilish(self) -> None:
        """Eng eski yozuv `last_id` dan keyin boshlansa — orada hodisa yo'qolgan."""
        client = FakeRedis([entry(9), entry(8), entry(7)])
        events, gap = _run(client, last_id=3)
        assert [e["id"] for e in events] == [7, 8, 9]
        assert gap is True

    def test_last_id_yoq_bolsa_uzilish_yoq(self) -> None:
        """Birinchi ulanish: `Last-Event-ID` yo'q, ya'ni yo'qolgan narsa ham yo'q."""
        client = FakeRedis([entry(9), entry(8)])
        events, gap = _run(client, last_id=0)
        assert len(events) == 2
        assert gap is False

    def test_buzuq_yozuv_qolganini_toxtatmaydi(self) -> None:
        """Bitta buzuq yozuv butun replay'ni yiqitmasligi kerak."""
        client = FakeRedis([entry(4), "{buzuq", entry(3)])
        events, _ = _run(client, last_id=2)
        assert [e["id"] for e in events] == [3, 4]

    def test_bosh_bufer(self) -> None:
        events, gap = _run(FakeRedis([]), last_id=5)
        assert events == []
        assert gap is False


class TestPublish:
    """Nashr yiqilsa ham chaqiruvchi davom etishi SHART (ADR-0029 §13).

    Aks holda Redis nosozligi `drain_results` ni to'xtatardi va boshqa
    foydalanuvchilarning verdiktlari ham yozilmasdi — ya'ni bitta
    xizmatning ishlamasligi butun sud zanjirini yiqitardi.
    """

    def test_redis_yiqilsa_none_qaytadi(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def boom() -> Any:
            raise ConnectionError("redis yo'q")

        monkeypatch.setattr(bus, "_client", boom)
        assert bus.publish("rw:rt:user:1", "verdict", {"a": 1}) is None


def _run(client: FakeRedis, last_id: int) -> tuple[list[dict[str, Any]], bool]:
    """`replay_after` ni sinxron testdan chaqiradi.

    ⚠️ `asyncio.run` ATAYLAB: `pytest-asyncio` bog'liqligi shart emas, ya'ni
    bu test CI'da qo'shimcha plagin talab qilmaydi.
    """
    return asyncio.run(bus.replay_after(client, "rw:rt:user:1", last_id))
