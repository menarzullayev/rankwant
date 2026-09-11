"""Unvonlar — Contests reytingidan (ADR-0018).

Nomlar bu yerda EMAS, i18n'da (`title.<kod>`): mavzu almashtirilsa faqat
tarjimalar o'zgaradi. Bu yerda — kod, quyi chegara va rang pog'onasi.
"""

from __future__ import annotations

from typing import Any, TypedDict

#: (quyi chegara, kod), o'sish tartibida. Pog'ona = indeks + 1.
#: Boshlang'ich reyting 1400 (`User.rating_contest`) — birinchi
#: musobaqadan keyin odam 3-pog'ona atrofida turadi, Codeforces'dagi
#: kabi ikki pog'ona pastga ham, yuqoriga ham joy qoladi.
TITLES: tuple[tuple[int, str], ...] = (
    (0, "kvark"),
    (1200, "foton"),
    (1400, "elektron"),
    (1600, "proton"),
    (1800, "atom"),
    (2000, "molekula"),
    (2200, "kristal"),
    (2400, "yulduz"),
    (2700, "galaktika"),
)


class Title(TypedDict):
    code: str
    level: int


def title_for(rating: int, rated_contests: int) -> Title | None:
    """Reytingli musobaqasiz odam unvonsiz: boshlang'ich 1400 hali hech narsa aytmaydi."""
    if rated_contests <= 0:
        return None
    level = 0
    for i, (floor, _code) in enumerate(TITLES):
        if rating >= floor:
            level = i
    return {"code": TITLES[level][1], "level": level + 1}


def user_title(user: Any) -> Title | None:
    return title_for(user.rating_contest, user.rated_contest_count)


def bands() -> list[dict[str, Any]]:
    """Reyting grafigi uchun chegaralar — yuqorisi ochiq."""
    return [
        {
            "code": code,
            "level": i + 1,
            "min": floor,
            "max": TITLES[i + 1][0] if i + 1 < len(TITLES) else None,
        }
        for i, (floor, code) in enumerate(TITLES)
    ]
