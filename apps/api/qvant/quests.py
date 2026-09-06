"""Quest dvigateli — ADR-0002 earn jadvali.

Quest kodlari hodisalarga bog'langan. `period_key` anti-farm kaliti:
uniq cheklov bazada, ya'ni bir davrda ikki marta mukofot berish
kod xatosi bilan ham mumkin emas.
"""

from __future__ import annotations

import logging
from datetime import date

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.models import User
from qvant import ledger
from qvant.models import QvantQuest, QvantTransaction, UserQuestCompletion

log = logging.getLogger(__name__)

# ── Quest kodlari ────────────────────────────────────────────────────
DAILY_SOLVE = "daily_solve"
DAILY_THREE_AC = "daily_three_ac"
CONTEST_FINISH = "contest_finish"
WEEKLY_MARATHON = "weekly_marathon"
PROFILE_COMPLETE = "profile_complete"
STREAK_7 = "streak_7"
STREAK_30 = "streak_30"
STREAK_365 = "streak_365"

#: ADR-0002 earn jadvali. `code → (tur, mukofot, uz nomi)`
#:
#: DIQQAT: ADR «kunning masalasini yechish» deydi. Masala-of-the-day
#: funksiyasi PRD da yo'q, shuning uchun quest «kuniga kamida bitta
#: masala yechish» sifatida amalga oshirilgan. Kunlik masala qo'shilsa,
#: quest o'sha masalaga bog'lanadi — mukofot va davr o'zgarmaydi.
CATALOGUE: dict[str, tuple[str, int, str]] = {
    DAILY_SOLVE: (QvantQuest.Type.DAILY, 10, "Kuniga kamida bitta masala yeching"),
    DAILY_THREE_AC: (QvantQuest.Type.DAILY, 15, "Bir kunda 3 ta masala yeching"),
    CONTEST_FINISH: (QvantQuest.Type.WEEKLY, 30, "Reytingli musobaqani yakunlang"),
    WEEKLY_MARATHON: (QvantQuest.Type.WEEKLY, 100, "Haftalik marafonni yakunlang"),
    PROFILE_COMPLETE: (QvantQuest.Type.ACHIEVEMENT, 50, "Profilingizni to'ldiring"),
    STREAK_7: (QvantQuest.Type.ACHIEVEMENT, 50, "7 kunlik streak"),
    STREAK_30: (QvantQuest.Type.ACHIEVEMENT, 250, "30 kunlik streak"),
    STREAK_365: (QvantQuest.Type.ACHIEVEMENT, 2000, "365 kunlik streak"),
}

#: Streak yutuqlari shiftdan ozod (ADR-0002)
STREAK_QUESTS = frozenset({STREAK_7, STREAK_30, STREAK_365})


def day_key(when: date | None = None) -> str:
    return (when or timezone.localdate()).isoformat()


def week_key(when: date | None = None) -> str:
    d = when or timezone.localdate()
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


@transaction.atomic
def award(user: User, code: str, period_key: str, *, ref_id: str = "") -> int:
    """Questni bir marta mukofotlaydi. Qaytaradi: berilgan Qvant (0 = berilmadi).

    Ikki himoya qatlami:
      1. `UserQuestCompletion` uniq cheklovi — bir davrda bir marta
      2. `ledger.credit` kunlik shifti — ADR-0002 anti-farm
    """
    try:
        quest = QvantQuest.objects.get(code=code, is_active=True)
    except QvantQuest.DoesNotExist:
        log.warning("noma'lum yoki o'chirilgan quest: %s", code)
        return 0

    reason = (
        QvantTransaction.Reason.STREAK if code in STREAK_QUESTS else QvantTransaction.Reason.QUEST
    )

    try:
        with transaction.atomic():
            completion = UserQuestCompletion.objects.create(
                user=user, quest=quest, period_key=period_key, awarded=0
            )
    except IntegrityError:
        return 0  # shu davrda allaqachon berilgan

    tx = ledger.credit(
        user,
        quest.reward,
        reason,
        ref_type="quest",
        ref_id=ref_id or code,
        respect_cap=code not in STREAK_QUESTS,
    )
    granted = tx.amount if tx else 0
    # Shift tufayli kamroq berilgan bo'lsa ham, quest BAJARILGAN deb qoladi:
    # Activity reyting bajarilgan quest sonini sanaydi, Qvant miqdorini emas.
    completion.awarded = granted
    completion.save(update_fields=["awarded"])
    return granted


def on_accepted(user: User, *, ac_count_today: int) -> list[str]:
    """AC olingandan keyin — kunlik questlarni tekshiradi."""
    key = day_key()
    granted: list[str] = []
    if award(user, DAILY_SOLVE, key):
        granted.append(DAILY_SOLVE)
    if ac_count_today >= 3 and award(user, DAILY_THREE_AC, key):
        granted.append(DAILY_THREE_AC)
    return granted


def on_contest_finished(user: User, contest_slug: str) -> int:
    """Reytingli musobaqa yakunlangach — contest boshiga bir marta."""
    return award(user, CONTEST_FINISH, f"contest:{contest_slug}", ref_id=contest_slug)


def on_streak_reached(user: User, streak: int) -> list[str]:
    """Streak bosqichlari.

    7 kunlik yutuq HAR 7 kunda beriladi (ADR-0002: «har 7 kunlik
    bosqichda»), 30 va 365 esa davr boshiga bir marta.
    """
    granted: list[str] = []
    if streak > 0 and streak % 7 == 0 and award(user, STREAK_7, f"streak-7:{streak}"):
        granted.append(STREAK_7)
    if streak == 30 and award(user, STREAK_30, "streak-30"):
        granted.append(STREAK_30)
    if streak == 365 and award(user, STREAK_365, "streak-365"):
        granted.append(STREAK_365)
    return granted


def on_profile_completed(user: User) -> int:
    """Umrbod bir marta."""
    return award(user, PROFILE_COMPLETE, "once")


def profile_is_complete(user: User) -> bool:
    return bool(user.display_name and user.bio and user.avatar_url)


def sync_catalogue() -> int:
    """Katalogni bazaga yozadi — migratsiya emas, ma'lumot."""
    for code, (qtype, reward, title) in CATALOGUE.items():
        QvantQuest.objects.update_or_create(
            code=code,
            defaults={"type": qtype, "reward": reward, "title_uz": title, "is_active": True},
        )
    return len(CATALOGUE)
