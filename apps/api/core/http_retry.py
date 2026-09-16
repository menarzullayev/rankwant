"""Tashqi HTTP chaqiruvlari — 429 va vaqtinchalik xatolar uchun qayta urinish.

Nega kerak: barcha tashqi chaqiriqlar stdlib `urllib` bilan qilingan
(`requests`/`httpx` qo'shilmagan — ataylab, Docker image'ga yangi
bog'liqlik kirmasin). Yetti chaqiruv joyidan faqat **bittasida**
(`problems/kep.py`) o'zining kichik 429 tsikli bor edi, qolganlarida
qayta urinish umuman yo'q edi: Telegram, OAuth provayderlari, Turnstile,
email zanjiri, tashqi profil saytlari — hammasi birinchi 429 da yiqilardi.

Qoida:
  * `Retry-After` sarlavhasi bo'lsa — u hurmat qilinadi (yuqori chegara
    bilan: provayder 1 soat kut degan bo'lsa, navbat 1 soatga qotib
    qolmasin);
  * bo'lmasa eksponensial backoff — 0.5s, 1s, 2s … (yuqori chegara 8s);
  * har backoff'ga ozgina jitter qo'shiladi: yuzlab ishchi bir vaqtda
    qayta urinib, cheklovni yana o'zi yasab qo'ymasin;
  * **faqat** 429/5xx va tarmoq xatolari qayta uriniladi. 4xx — bizning
    so'rov noto'g'ri, qayta urinish uni to'g'rilamaydi.
"""

from __future__ import annotations

import logging
import random
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

log = logging.getLogger(__name__)

#: Qayta urinish ma'noli bo'lgan holatlar. 4xx (401/403/404/422) shu
#: ro'yxatda YO'Q — ular so'rov yoki kalit xatosi.
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})

#: Jami urinish = `RETRIES + 1`.
RETRIES = 2
BACKOFF = 0.5
MAX_BACKOFF = 8.0
#: `Retry-After` shu qiymatdan oshsa, u o'rniga `MAX_BACKOFF` ishlatiladi:
#: uzun kutish navbatni/qismni qotirib qo'yadi.
MAX_RETRY_AFTER = 30.0

_JITTER = 0.25


def _backoff(attempt: int, base: float, cap: float = MAX_BACKOFF) -> float:
    """Eksponensial kutish + jitter. `attempt` 0 dan boshlanadi.

    `cap` alohida: interaktiv yo'llar (Turnstile, OAuth) 2 soniyadan
    oshmasligi kerak, KEP importi esa 5 soniyadan boshlanadi.
    """
    wait = min(base * (2**attempt), cap)
    return float(wait + random.uniform(0, wait * _JITTER))


def _retry_after(headers: Any, attempt: int, base: float, cap: float = MAX_BACKOFF) -> float:
    """`Retry-After` ni soniyaga aylantiradi. Yo'q/bo'sh bo'lsa — backoff.

    Sarlavha ikki shaklda bo'ladi: soniya (`Retry-After: 30`) yoki HTTP
    sana (`Retry-After: Wed, 21 Oct 2026 07:28:00 GMT`). Ikkisi ham
    qo'llab-quvvatlanadi, chunki provayderlar ikkalasini ham yuboradi.
    """
    raw = None
    try:
        raw = headers.get("Retry-After") if headers else None
    except Exception:  # sarlavha obyektiga ishonch yo'q (test dublikatori ham)
        raw = None
    if raw:
        try:
            return max(0.0, min(float(str(raw).strip()), MAX_RETRY_AFTER))
        except ValueError:
            pass
        try:
            when = parsedate_to_datetime(str(raw))
        except (TypeError, ValueError):
            when = None
        if when is not None:
            if when.tzinfo is None:
                when = when.replace(tzinfo=UTC)
            delta = (when - datetime.now(tz=UTC)).total_seconds()
            return max(0.0, min(delta, MAX_RETRY_AFTER))
    return _backoff(attempt, base, cap)


def open_with_retry(
    request: urllib.request.Request,
    *,
    timeout: float,
    retries: int = RETRIES,
    backoff: float = BACKOFF,
    max_backoff: float = MAX_BACKOFF,
    opener: urllib.request.OpenerDirector | None = None,
    label: str = "",
) -> Any:
    """`urlopen` — 429/5xx va tarmoq xatosida qayta urinib.

    `label` log uchun: manzil ichida token bo'lishi mumkin (Telegram bot
    tokeni aynan URL da), shuning uchun chaqiruvchi xavfsiz nom beradi.

    Qaytgan obyekt — kontekst boshqaruvchisi (`with ... as resp`).
    Barcha urinishlar tugagach ham xato bo'lsa, oxirgi istisno ko'tariladi.
    """
    url = label or getattr(request, "full_url", "?")
    call = opener.open if opener is not None else urllib.request.urlopen

    for attempt in range(retries + 1):
        last = attempt == retries
        try:
            return call(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code not in RETRY_STATUSES or last:
                raise
            wait = _retry_after(exc.headers, attempt, backoff, max_backoff)
            log.warning(
                "tashqi HTTP %s: %s — %d/%d urinishdan keyin %.1fs kutib qayta urinish",
                exc.code,
                url,
                attempt + 1,
                retries + 1,
                wait,
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if last:
                raise
            wait = _backoff(attempt, backoff, max_backoff)
            log.warning(
                "tashqi HTTP tarmoq xatosi: %s (%s) — %d/%d, %.1fs kutib qayta urinish",
                url,
                exc,
                attempt + 1,
                retries + 1,
                wait,
            )
        time.sleep(wait)

    raise RuntimeError("yetib bo'lmadi")  # pragma: no cover — tsikl har doim qaytadi
