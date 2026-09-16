"""Hack siyosatlari — ADR-0020 ning «bitta dvigatel, to'rtta siyosat» jadvali.

Siyosat kod emas, KONFIGURATSIYA: to'rttasi shu yerdagi bitta jadvalda
e'lon qilinadi, dvigatel esa faqat shu maydonlarni o'qiydi. Yangi musobaqa
turi yangi modul emas, yangi qator talab qiladi (ADR-0020, 1-tamoyil).

To'rt siyosatning farqi atigi to'rt o'lchovda: oyna qachon ochiq, kim hack
qila oladi, ball beriladimi va natija test to'plami bilan nima qiladi.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


class Window:
    """Oyna qachon ochiq (`Policy.window`)."""

    #: Musobaqa davomida — o'z xonasida, lock qilingan masalada
    CONTEST = "contest"
    #: `end_at` dan keyin, hack oynasi yopilgunicha
    AFTER_CONTEST = "after_contest"
    #: Reyting qo'llangach — uphack
    AFTER_RATING = "after_rating"
    #: Amaliyot: musobaqaga bog'lanmagan, doim ochiq
    ALWAYS = "always"


class AddsTest:
    """Muvaffaqiyatli hack testi asosiy to'plamga QACHON qo'shiladi."""

    NEVER = "never"
    #: Darhol: oyna tushunchasi yo'q (amaliyot, uphack)
    IMMEDIATE = "immediate"
    #: Oyna yopilganda, reytingdan OLDIN (ADR-0020, 7-tamoyil)
    ON_CLOSE = "on_close"


@dataclass(frozen=True)
class Policy:
    code: str
    label: str
    window: str
    #: Faqat o'z xonasidagi ishtirokchining yechimi (contest_room)
    room_only: bool = False
    #: Masalani «lock» qilgan bo'lish sharti (contest_room)
    needs_lock: bool = False
    #: Ishonchli foydalanuvchi sharti (uphack)
    trusted_only: bool = False
    #: Jadvalga qo'shiladigan ball — Codeforces Div 1/2 modeli
    success_points: int = 0
    failure_points: int = 0
    #: Amaliyotda mukofot Qvant bilan beriladi — faqat ledger orqali (ADR-0002)
    qvant_reward: int = 0
    adds_test: str = AddsTest.NEVER
    #: Oyna yopilganda o'sha masaladagi barcha `AC` qayta tekshiriladimi
    rejudge_on_close: bool = False
    #: Natija musobaqa jadvaliga ta'sir qiladimi
    affects_standings: bool = False


#: Codeforces Div 1/2: raund davomida, o'z xonasi (~40 kishi), lock shart,
#: +100 / −50 va jadvalga darhol ta'sir qiladi.
CONTEST_ROOM: Final = Policy(
    code="contest_room",
    label="Musobaqa xonasi",
    window=Window.CONTEST,
    room_only=True,
    needs_lock=True,
    success_points=100,
    failure_points=-50,
    adds_test=AddsTest.ON_CLOSE,
    rejudge_on_close=True,
    affects_standings=True,
)

#: Educational / Div 3-4 uslubi: musobaqa tugagach ochiq oyna. Ball yo'q —
#: rag'bat sof sport. Oyna yopilgach testlar qo'shiladi, `AC` lar qayta
#: tekshiriladi va SHUNDAN KEYIN reyting qo'llanadi.
OPEN_PHASE: Final = Policy(
    code="open_phase",
    label="Ochiq faza",
    window=Window.AFTER_CONTEST,
    adds_test=AddsTest.ON_CLOSE,
    rejudge_on_close=True,
    affects_standings=True,
)

#: KEP.uz modeli: musobaqaga bog'lanmagan amaliyot. Mukofot — Qvant;
#: kunlik emissiya chegarasi ledgerda (ADR-0002) va u farmni to'sadi.
PRACTICE: Final = Policy(
    code="practice",
    label="Amaliyot",
    window=Window.ALWAYS,
    qvant_reward=20,
    adds_test=AddsTest.IMMEDIATE,
)

#: Musobaqadan keyingi uzoq oyna, faqat ishonchli foydalanuvchi uchun.
#: Jadval va reyting O'ZGARMAYDI: ular allaqachon yakunlangan.
UPHACK: Final = Policy(
    code="uphack",
    label="Uphack",
    window=Window.AFTER_RATING,
    trusted_only=True,
    adds_test=AddsTest.IMMEDIATE,
)

POLICIES: Final[dict[str, Policy]] = {
    p.code: p for p in (CONTEST_ROOM, OPEN_PHASE, PRACTICE, UPHACK)
}

#: Model `choices` uchun — kod va yorliq shu jadvaldan olinadi, ya'ni
#: siyosat qo'shilsa migratsiya ham, UI ham bir manbadan yangilanadi.
CHOICES: Final = [(p.code, p.label) for p in POLICIES.values()]


def get(code: str) -> Policy | None:
    """Kod bo'yicha siyosat. Notanish kod — `None`, jimgina standart EMAS."""
    return POLICIES.get(code)
