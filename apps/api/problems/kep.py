"""KEP.uz arxivini o'qish — mijoz va xaritalash.

Import KEP egalarining ruxsati bilan qilinadi. Ochiq API masala matni,
namunalar, teglar, limitlar, tillar va mualliflarni beradi; YASHIRIN
TESTLAR va yechim tahlili esa faqat autentifikatsiya bilan ochiladi.
Shu sababli import qilingan masala QORALAMA bo'lib tushadi: testsiz
uni tekshirib bo'lmaydi, ommaga chiqarish esa yolg'on va'da bo'lardi.

Xaritalash tarmoqqa bog'liq emas — `to_fields()` ni oddiy lug'at bilan
sinash mumkin, shuning uchun testda KEP ga so'rov ketmaydi.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from collections.abc import Iterator
from typing import Any

from django.utils.text import slugify

from problems.html_to_markdown import html_to_markdown
from problems.models import DIFFICULTY_MAX, DIFFICULTY_MIN, DIFFICULTY_STEP

SITE = os.environ.get("KEP_SITE", "https://kep.uz")
BASE = os.environ.get("KEP_API_BASE", f"{SITE}/api")
#: O'zimizni tanitamiz — trafik kimdan kelayotgani KEP loglarida ko'rinsin.
USER_AGENT = "RankWant-Importer/1.0 (+https://rankwant.uz)"
TIMEOUT = 30

#: KEP reytingi 100–2400, bizniki 800–3500. Ikki uchni bog'lab chiziqli
#: o'tkazamiz: 100 → 800, 2400 → 3200. Yuqoridagi 3300–3500 ataylab bo'sh
#: qoladi — import qilingan masala eng qiyin darajani egallab olmasin.
SOURCE_MIN, SOURCE_MAX = 100, 2400
TARGET_MIN, TARGET_MAX = 800, 3200

#: KEP til kodi → bizning `Language.code`. Qolganlari (rs, go, php, hs…)
#: judge obrazimizda yo'q; ular tashlab ketiladi, masala esa bor
#: tillarda yechiladi.
LANGUAGES = {"py": "py313", "cpp": "cpp23", "java": "java21"}


def fetch(path: str, **params: Any) -> Any:
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.load(response)


def tags() -> list[dict[str, Any]]:
    return list(fetch("/tags/"))


def problem(kep_id: int) -> dict[str, Any]:
    return dict(fetch(f"/problems/{kep_id}/"))


def user(username: str) -> dict[str, Any]:
    return dict(fetch(f"/users/{username}/"))


def iter_summaries(page_size: int = 50) -> Iterator[dict[str, Any]]:
    """Ro'yxatni sahifama-sahifa aylanadi (eng yangisidan boshlab)."""
    page = 1
    while True:
        payload = fetch("/problems/", page=page, pageSize=page_size)
        rows = payload.get("data") or []
        yield from rows
        if not rows or page >= payload.get("pagesCount", 0):
            return
        page += 1


def map_difficulty(rating: int | None) -> int:
    """KEP reytingini bizning shkalaga o'tkazadi."""
    if not rating:
        return DIFFICULTY_MIN
    ratio = (rating - SOURCE_MIN) / (SOURCE_MAX - SOURCE_MIN)
    scaled = TARGET_MIN + ratio * (TARGET_MAX - TARGET_MIN)
    stepped = DIFFICULTY_STEP * round(scaled / DIFFICULTY_STEP)
    return max(DIFFICULTY_MIN, min(DIFFICULTY_MAX, stepped))


def make_slug(title: str, kep_id: int, taken: set[str]) -> str:
    """O'qiladigan, lekin takrorlanmaydigan slug.

    Sarlavha lotin bo'lmasa yoki band bo'lsa KEP raqami qo'shiladi —
    shunda ham havola bir marta beriladi va keyin o'zgarmaydi.
    """
    base = slugify(title)[:80].strip("-") or f"masala-{kep_id}"
    if base in taken:
        base = f"{base}-{kep_id}"[:100]
    taken.add(base)
    return base


def to_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Detal javobidan `Problem` maydonlarini yasaydi.

    `hasChecker` bu yerda ISHLATILMAYDI: KEP uni `a+b` da ham `true`
    qiladi, ya'ni u maxsus checker emas, «tekshiruvchi sozlangan»
    degani. Uni `checker_type` ga o'tkazish hamma masalani noto'g'ri
    maxsus qilib qo'yardi.
    """
    memory_mb = payload.get("memoryLimit") or 256
    return {
        "title": (payload.get("title") or "").strip()[:200],
        "statement": html_to_markdown(payload.get("body")),
        "input_format": html_to_markdown(payload.get("inputData")),
        "output_format": html_to_markdown(payload.get("outputData")),
        "note": html_to_markdown(payload.get("comment")),
        "difficulty": map_difficulty(payload.get("problemRating")),
        "source_rating": payload.get("problemRating") or None,
        "time_limit_ms": payload.get("timeLimit") or 1000,
        "memory_limit_kb": memory_mb * 1024,
        "partial_scoring": bool(payload.get("partialSolvable")),
        "likes_count": payload.get("likesCount") or 0,
        "dislikes_count": payload.get("dislikesCount") or 0,
        "image": payload.get("image") or "",
        "source": "KEP.uz",
        "source_url": f"{SITE}/problems/{payload['id']}",
    }


def language_limits(entry: dict[str, Any], memory_mb_default: int) -> dict[str, Any]:
    """`availableLanguages` yozuvidan ustma-ust limitlar.

    `null` — «masala limiti ishlaydi», shuning uchun u NULL bo'lib
    qoladi va bizning modelda ham xuddi shu ma'noni bildiradi.
    """
    memory_mb = entry.get("memoryLimit")
    return {
        "time_limit_ms": entry.get("timeLimit") or None,
        "memory_limit_kb": (memory_mb or memory_mb_default) * 1024 if memory_mb else None,
        "code_template": (entry.get("codeTemplate") or "").replace("\r\n", "\n").strip(),
    }
