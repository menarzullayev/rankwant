"""4 reyting formulasi — 04-prd 🔒 § Reyting formulalari.

Bu modul SOF funksiyalardan iborat: DB ga tegmaydi, shuning uchun
property-based test bilan to'liq qamrab olinadi (10-operations § test).

Principle #2: formulalar ochiq. Bu yerdagi hech narsa yashirin emas.
"""

from __future__ import annotations

import math

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

    deltas: list[float] = []
    for i, rating in enumerate(ratings):
        others = ratings[:i] + ratings[i + 1 :]
        s = seed(rating, others)
        target = math.sqrt(s * ranks[i])
        r_star = rating_for_seed(target, others)
        deltas.append((r_star - rating) / 2.0)

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
