"""Hodisa avtobusi — Redis pub/sub (ADR-0029 §6).

Nega alohida modul: nashr qiluvchi tomon **sinxron** (Celery worker,
`judging.drain_results`), obunachi tomon esa **asinxron** (ASGI,
`realtime.views`). Ikkisi bir xil kanal nomlari va bir xil replay
formatini bilishi shart — usiz nom bir joyda o'zgarib, ikkinchisida
jimgina ishlamay qolardi (oqim ochiladi, lekin hech qachon hodisa
kelmaydi va buni faqat foydalanuvchi sezadi).

⚠️ **Pub/sub SAQLANMAYDI.** Obunachi uzilganda hodisa yo'qoladi. Shu
sababli har bir hodisa qisqa **replay buferiga** ham yoziladi va mijoz
`Last-Event-ID` bilan qayta ulanganda o'sha buferdan to'ldiriladi
(ADR-0029 §9). Bufer — kafolat emas, **imkoniyat**: u yo'q bo'lsa
server `resync` yuboradi va mijoz holatni REST dan qayta o'qiydi.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from django.conf import settings
from redis import Redis

log = logging.getLogger(__name__)

#: Kanal nomlari. ⚠️ `user` kanali SHAXSIY: nom **sessiyadan** olinadi,
#: mijozdan emas (ADR-0029 §7). Aks holda begona odamning verdiktini
#: kuzatish mumkin bo'lardi (IDOR).
USER_CHANNEL = "rw:rt:user:{user_id}"
#: Ommaviy jadval kanali. ⚠️ Bu kanal **jadvalning o'zini tashimaydi** —
#: faqat versiya belgisi (ADR-0029 §3). Sabab `docs/10` o'lchovi: 110 000
#: ochiq ulanishda hujjatni oqim orqali tashish chekka kesh bergan narsani
#: qimmatlashtiradi.
STANDINGS_CHANNEL = "rw:rt:standings:{contest_id}"

#: Replay buferining chuqurligi va umri. Chuqurligi qayta ulanish
#: oynasidan kelib chiqadi: mijoz odatda soniyalarda qaytadi, 50 hodisa
#: esa gavjum musobaqada ham shu oynani qoplaydi.
REPLAY_MAX = 50
REPLAY_TTL_S = 300


def user_channel(user_id: int) -> str:
    return USER_CHANNEL.format(user_id=user_id)


def standings_channel(contest_id: int) -> str:
    return STANDINGS_CHANNEL.format(contest_id=contest_id)


def _client() -> Redis:
    """Sinxron klient — faqat nashr tomoni uchun.

    ⚠️ Har chaqiruvda yangi obyekt: Celery worker uzoq yashaydi va
    global ulanish uzilib qolsa (Redis restart, `maxmemory` eviction)
    u jimgina o'lik bo'lib qolardi.
    """
    return Redis.from_url(settings.REDIS_URL)


def publish(channel: str, event: str, payload: dict[str, Any]) -> int | None:
    """Hodisani kanalga yuboradi va replay buferiga yozadi.

    Qaytaradi: hodisa raqami (mijoz `Last-Event-ID` da shuni ko'radi).

    ⚠️ **Nashr yiqilsa ham chaqiruvchi yiqilmasligi kerak.** Verdikt allaqachon
    bazaga yozilgan; Redis nosozligi tufayli `drain_results` istisno bersa
    navbat to'xtab qolardi va boshqa foydalanuvchilarning natijalari ham
    yozilmasdi. Shuning uchun xato log qilinadi va `None` qaytadi —
    foydalanuvchi jonli yangilanishni ko'rmaydi, lekin sahifani yangilasa
    natija joyida bo'ladi (ADR-0029 §13: oqim — optimallashtirish).
    """
    blob: str | None = None
    try:
        client = _client()
        seq_key = f"rw:rt:seq:{channel}"
        replay_key = f"rw:rt:replay:{channel}"
        seq = client.incr(seq_key)
        blob = json.dumps({"id": seq, "event": event, "data": payload}, ensure_ascii=False)
        pipe = client.pipeline()
        pipe.expire(seq_key, REPLAY_TTL_S)
        pipe.lpush(replay_key, blob)
        pipe.ltrim(replay_key, 0, REPLAY_MAX - 1)
        pipe.expire(replay_key, REPLAY_TTL_S)
        pipe.publish(channel, blob)
        pipe.execute()
        return int(seq)
    except Exception:
        log.exception("hodisani nashr qilib bo'lmadi: %s / %s", channel, event)
        return None


async def replay_after(
    client: Any, channel: str, last_id: int
) -> tuple[list[dict[str, Any]], bool]:
    """`last_id` dan keyingi hodisalarni buferdan qaytaradi.

    Qaytaradi: `(hodisalar, uzilish_bor)`. `uzilish_bor` rost bo'lsa bufer
    yetarli emas — mijoz `resync` oladi va holatni REST dan qayta o'qiydi.

    ⚠️ Bu **asinxron** klientni kutadi (`redis.asyncio`), chunki SSE
    ko'rinishi ASGI ostida ishlaydi va sinxron chaqiruv butun event
    loop'ni bloklaydi.
    """
    raw = await client.lrange(f"rw:rt:replay:{channel}", 0, -1)
    items: list[dict[str, Any]] = []
    for entry in raw:
        try:
            items.append(json.loads(entry))
        except (TypeError, ValueError):
            continue  # buzuq yozuv butun replay'ni to'xtatmasin
    items.sort(key=lambda item: item["id"])
    oldest = items[0]["id"] if items else None
    #: Bufer to'lgan bo'lsa va eng eski yozuv `last_id` dan keyin
    #: boshlansa — oradagi hodisalar allaqachon siqib chiqarilgan.
    gap = bool(last_id and oldest is not None and oldest > last_id + 1)
    kept = [item for item in items if item["id"] > last_id]
    return kept, gap
