"""4 reyting formulasi — 04-prd 🔒 § Reyting formulalari.

Bu modul SOF funksiyalardan iborat: DB ga tegmaydi, shuning uchun
property-based test bilan to'liq qamrab olinadi (10-operations § test).

Principle #2: formulalar ochiq. Bu yerdagi hech narsa yashirin emas.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable

# ── Skills — ADR-0006, ADR-0007 ──────────────────────────────────────
SKILLS_DECAY = 0.95


def skills_rating(difficulties: list[int]) -> int:
    """Skills = round(Σ pᵢ × 0.95^(i−1)), kamayish tartibida saralangan.

    `pᵢ` — masalaning JORIY qiyinligi (ADR-0007).

    Isbotlangan xossalar:
      * monoton — yangi masala qo'shish natijani kamaytirmaydi
      * cheklangan — eng katta masaladan 20 baravardan oshmaydi
      * ~45 masaladan keyin bir xil qiyinlikda to'yinadi
    """
    total = 0.0
    for i, points in enumerate(sorted(difficulties, reverse=True)):
        total += points * (SKILLS_DECAY**i)
    return round(total)


# ── Contests — Codeforces uslubi ─────────────────────────────────────
INITIAL_CONTEST_RATING = 1400
RATING_FLOOR = 0
NEW_USER_CONTESTS = 6
NEW_USER_VOLATILITY = 1.5
MIN_RATED_PARTICIPANTS = 10


def win_probability(rating_a: int, rating_b: int) -> float:
    """P(a beats b) — Elo, 400 shkalasi."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def seed(rating: int, others: list[int]) -> float:
    """Kutilgan o'rin: 1 + Σ P(j beats i)."""
    return 1.0 + sum(win_probability(other, rating) for other in others)


def _seed_table(ratings: list[int]) -> Callable[[int], float]:
    """`r` reytingi uchun 1 + Σ P(j beats r) — barcha ishtirokchilar bo'yicha.

    Yig'indi noyob reyting bo'yicha bir marta hisoblanadi va keshlanadi.
    Buning ma'nosi bor, chunki binar qidiruv `[1, 8000]` da doim bir xil
    o'rta nuqtalardan boshlaydi: 10 000 kishining ~130 000 hisoblashi
    amalda ~1 700 ta noyob qiymatga tushadi.

    O'lchandi: 3 200 ishtirokchida 12.80 s → 0.19 s, natijalar bir xil.
    """
    histogram = sorted(Counter(ratings).items())
    cache: dict[int, float] = {}

    def total(r: int) -> float:
        got = cache.get(r)
        if got is None:
            got = cache[r] = 1.0 + sum(c * win_probability(v, r) for v, c in histogram)
        return got

    return total


def contest_seeds(ratings: list[int]) -> list[float]:
    """Har bir ishtirokchining kutilgan o'rni — `seed` ning partiyaviy shakli.

    Har biriga `seed()` ni alohida chaqirish O(n²) bo'lardi. Bu yerda
    ishtirokchining o'z hissasi (P(i beats i) = 0.5) umumiy yig'indidan
    ayiriladi — natija `seed(rᵢ, o'zidan boshqalar)` bilan bir xil.
    """
    total = _seed_table(ratings)
    return [total(r) - 0.5 for r in ratings]


def rating_for_seed(target_seed: float, others: list[int]) -> int:
    """`seed = target_seed` beradigan reyting — binar qidiruv."""
    lo, hi = 1, 8000
    while lo < hi:
        mid = (lo + hi) // 2
        if seed(mid, others) > target_seed:
            lo = mid + 1
        else:
            hi = mid
    return lo


def contest_deltas(
    ratings: list[int], ranks: list[int], contest_counts: list[int] | None = None
) -> list[int]:
    """Musobaqadan keyingi reyting o'zgarishlari.

    1. seedᵢ — kutilgan o'rin
    2. mᵢ = √(seedᵢ × rankᵢ) — geometrik o'rtacha
    3. R*ᵢ — mᵢ ga mos reyting
    4. dᵢ = (R*ᵢ − Rᵢ) / 2
    5. inflyatsiya tuzatishi: barcha dᵢ dan Σd/n ayiriladi
    """
    n = len(ratings)
    if n == 0:
        return []
    counts = contest_counts or [NEW_USER_CONTESTS] * n

    total = _seed_table(ratings)

    def r_star(target: float, own: int) -> int:
        """`seed = target` beradigan reyting — `rating_for_seed` ning
        keshdan foydalanadigan shakli (o'zi yig'indidan chiqariladi)."""
        lo, hi = 1, 8000
        while lo < hi:
            mid = (lo + hi) // 2
            if total(mid) - win_probability(own, mid) > target:
                lo = mid + 1
            else:
                hi = mid
        return lo

    deltas: list[float] = []
    for i, rating in enumerate(ratings):
        s = total(rating) - 0.5  # o'zining hissasi
        deltas.append((r_star(math.sqrt(s * ranks[i]), rating) - rating) / 2.0)

    # Musobaqa umumiy reytingni shishirmasligi kerak
    correction = sum(deltas) / n
    deltas = [d - correction for d in deltas]

    # Yangi foydalanuvchi tezroq o'z darajasiga chiqadi
    out: list[int] = []
    for i, d in enumerate(deltas):
        if counts[i] < NEW_USER_CONTESTS:
            d *= NEW_USER_VOLATILITY
        out.append(round(d))
    return out


def apply_floor(rating: int) -> int:
    return max(RATING_FLOOR, rating)


# ── Activity — Phase 1, ADR-0002 ─────────────────────────────────────
ACTIVITY_WINDOW_DAYS = 30
ACTIVITY_MAX = 510


def activity_rating(active_days: int, quests_done: int, streak_days: int) -> int:
    """Activity = 10×faol_kun + 5×quest + min(2×streak, 60), 30 kunlik oyna.

    Qvant BALANSI ataylab ishlatilmaydi: aks holda do'konda xarid qilish
    reytingni tushirardi va foydalanuvchi sarflashdan qo'rqardi (ADR-0002).
    """
    return 10 * active_days + 5 * quests_done + min(2 * streak_days, 60)


# ── Challenges — Phase 3 ─────────────────────────────────────────────
DUEL_K_NEW = 32
DUEL_K_ESTABLISHED = 16
DUEL_K_THRESHOLD = 10


def duel_delta(rating: int, opponent_rating: int, score: float, duels_played: int) -> int:
    """Klassik 1v1 Elo: R' = R + K(S − E)."""
    expected = win_probability(rating, opponent_rating)
    k = DUEL_K_NEW if duels_played < DUEL_K_THRESHOLD else DUEL_K_ESTABLISHED
    return round(k * (score - expected))
