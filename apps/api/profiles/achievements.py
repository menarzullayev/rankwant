"""Yutuqlar — katalog, qo'lga kiritish, noyoblik va bir martalik Qvant (ADR-0018).

Qvant faqat YANGI yutuq uchun va faqat ledger orqali (ADR-0002), kunlik
shiftga bo'ysunadi — `profile_complete` questi kabi. Streak va profil
yutuqlarining Qvant'i quest orqali beriladi, bu yerda ular faqat qayd
etiladi. Migratsiyada tiklangan tarixiy yutuqlar ham `awarded=0`.

Quest emas, alohida jadval: Activity reytingi 30 kundagi HAR bajarilgan
questni sanaydi (`qvant.services.activity_inputs`) — yutuq quest bo'lsa,
tarixiy yutuqlarni tiklash hammaning Activity'sini sun'iy oshirardi.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Count

from core.cache import cache_get, cache_set
from core.models import User
from profiles.models import UserAchievement
from qvant import ledger
from qvant.models import QvantTransaction

BRONZE, SILVER, GOLD = "bronze", "silver", "gold"
#: Daraja → Qvant.
REWARD = {BRONZE: 10, SILVER: 30, GOLD: 75}
PINNED_MAX = 3
RARITY_TTL = 10 * 60


@dataclass(frozen=True)
class Spec:
    group: str
    target: int
    tier: str
    #: Qvant quest orqali beriladi (streak, profil) — ikkinchi marta emas.
    quest_paid: bool = False


CATALOGUE: dict[str, Spec] = {
    f"{spec.group}-{spec.target}": spec
    for spec in (
        Spec("solve", 1, BRONZE),
        Spec("solve", 10, BRONZE),
        Spec("solve", 100, SILVER),
        Spec("solve", 500, GOLD),
        Spec("solve", 1000, GOLD),
        Spec("streak", 7, BRONZE, quest_paid=True),
        Spec("streak", 30, SILVER, quest_paid=True),
        Spec("streak", 365, GOLD, quest_paid=True),
        Spec("contest", 1, BRONZE),
        Spec("contest", 10, SILVER),
        Spec("contest", 50, GOLD),
        Spec("profile", 1, BRONZE, quest_paid=True),
    )
}
CONTEST_TARGETS = frozenset(spec.target for spec in CATALOGUE.values() if spec.group == "contest")


@transaction.atomic
def grant(user: User, code: str) -> int:
    """Yutuqni qayd etadi. Qaytaradi: berilgan Qvant (0 — allaqachon bor yoki quest to'lagan)."""
    spec = CATALOGUE[code]
    try:
        with transaction.atomic():
            row = UserAchievement.objects.create(user=user, code=code)
    except IntegrityError:
        return 0
    if spec.quest_paid:
        return 0
    tx = ledger.credit(
        user,
        REWARD[spec.tier],
        QvantTransaction.Reason.ACHIEVEMENT,
        ref_type="achievement",
        ref_id=code,
    )
    # Shift tufayli kam berilgan bo'lsa ham yutuq olingan hisoblanadi.
    row.awarded = tx.amount if tx else 0
    row.save(update_fields=["awarded"])
    return row.awarded


def _missing(user: User, group: str, reached: int) -> list[str]:
    have = set(
        UserAchievement.objects.filter(user=user, code__startswith=f"{group}-").values_list(
            "code", flat=True
        )
    )
    return [
        code
        for code, spec in CATALOGUE.items()
        if spec.group == group and reached >= spec.target and code not in have
    ]


def on_solved(user: User, *, streak: int) -> list[str]:
    """Yangi masala yechilgach (birinchi AC): masala va streak bosqichlari."""
    from ratings.models import UserSolvedProblem

    solved = UserSolvedProblem.objects.filter(user=user).count()
    codes = _missing(user, "solve", solved) + _missing(user, "streak", streak)
    for code in codes:
        grant(user, code)
    return codes


def on_rated_contest(user: User) -> list[str]:
    """Reytingli musobaqa hisoblangach.

    Sanoq bittalab oshadi — bosqichdan faqat unga TENG bo'lganda o'tiladi,
    ya'ni o'n ming ishtirokchining ko'pchiligi uchun so'rov ham yo'q.
    """
    if user.rated_contest_count not in CONTEST_TARGETS:
        return []
    codes = _missing(user, "contest", user.rated_contest_count)
    for code in codes:
        grant(user, code)
    return codes


def on_unsolved(user: User) -> list[str]:
    """Rejudge yechimni bekor qildi — ADR-0002 «rejudge da qaytarish».

    Sanoq bosqichdan tushsa, yutuq olib tashlanadi va uning Qvant'i
    qaytariladi. Streak yutuqlari tegilmaydi: streak ham tegilmaydi
    (`qvant.services.revoke_for_attempt`).
    """
    from ratings.models import UserSolvedProblem

    solved = UserSolvedProblem.objects.filter(user=user).count()
    lost = [
        row
        for row in UserAchievement.objects.filter(user=user, code__startswith="solve-")
        if row.code in CATALOGUE and CATALOGUE[row.code].target > solved
    ]
    for row in lost:
        ledger.take_back(user, row.awarded, ref_type="achievement", ref_id=row.code)
        row.delete()
    return [row.code for row in lost]


def rarity() -> dict[str, float]:
    """Har yutuq egalarining ulushi (%) — faol foydalanuvchilar orasida."""
    value: dict[str, float] | None = cache_get("ach:rarity")
    if value is None:
        total = User.objects.filter(is_active=True).count() or 1
        value = {
            row["code"]: round(row["n"] * 100 / total, 2)
            for row in UserAchievement.objects.filter(user__is_active=True)
            .values("code")
            .annotate(n=Count("id"))
        }
        cache_set("ach:rarity", value, RARITY_TTL)
    return value


def rows(user: User) -> list[dict[str, Any]]:
    """Profil tabidagi ro'yxat: jarayon, daraja, noyoblik, qachon olingan."""
    from ratings.models import UserSolvedProblem

    have = dict(UserAchievement.objects.filter(user=user).values_list("code", "achieved_at"))
    progress = {
        "solve": UserSolvedProblem.objects.filter(user=user).count(),
        "streak": user.streak_count,
        "contest": user.rated_contest_count,
        "profile": 1 if "profile-1" in have else 0,
    }
    rare = rarity()
    pinned = set(user.pinned_achievements or [])
    out: list[dict[str, Any]] = []
    for code, spec in CATALOGUE.items():
        # Qayd yo'q, lekin shart bajarilgan (hook yiqilgan) — baribir olingan.
        done = code in have or progress[spec.group] >= spec.target
        out.append(
            {
                "code": code,
                "group": spec.group,
                "target": spec.target,
                "tier": spec.tier,
                "progress": spec.target if done else progress[spec.group],
                "done": done,
                "achieved_at": have.get(code),
                "rarity": rare.get(code, 0.0),
                "pinned": code in pinned,
            }
        )
    return out


def achieved(user: User) -> set[str]:
    return {row["code"] for row in rows(user) if row["done"]}


def pinned(user: User) -> list[dict[str, Any]]:
    """Profil kartasidagi uchta — egasi tanlagan va hali qo'lida bo'lganlari."""
    chosen = [code for code in user.pinned_achievements or [] if code in CATALOGUE]
    if not chosen:
        return []
    have = achieved(user)
    return [
        {
            "code": code,
            "group": CATALOGUE[code].group,
            "target": CATALOGUE[code].target,
            "tier": CATALOGUE[code].tier,
        }
        for code in chosen
        if code in have
    ]
