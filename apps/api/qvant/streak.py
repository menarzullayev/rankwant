"""Streak — ketma-ket faol kunlar. PRD P1-6.

Activity reytingining uchinchi komponenti va streak yutuqlarining manbai.
"""

from __future__ import annotations

from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from core.models import User
from qvant import quests


@transaction.atomic
def touch(user: User, when: date | None = None) -> tuple[int, list[str]]:
    """Foydalanuvchi faol bo'ldi (AC oldi). Qaytaradi: (streak, berilgan questlar).

    Qoidalar:
      * bir kunda bir necha AC — streak bir marta oshadi
      * bir kun tashlab ketilsa — streak 1 ga tushadi
      * `streak_freeze_until` amal qilsa — tashlangan kun kechiriladi
    """
    today = when or timezone.localdate()
    user = User.objects.select_for_update().get(pk=user.pk)

    last = user.last_active_date
    if last == today:
        return user.streak_count, []  # bugun allaqachon hisoblangan

    if last is None:
        user.streak_count = 1
    elif last == today - timedelta(days=1):
        user.streak_count += 1
    elif user.streak_freeze_until and user.streak_freeze_until >= today - timedelta(days=1):
        # Freeze bo'shliqni yopadi — streak saqlanadi va davom etadi.
        #
        # Taqqoslash TASHLANGAN kun bilan, qaytilgan kun bilan emas:
        # `apply_freeze` oxirgi tashlab ketish mumkin bo'lgan kunni
        # yozadi, foydalanuvchi esa undan KEYIN qaytadi. Ilgari bu yerda
        # `>= today` turardi va bir kunlik muzlatgich hech qachon
        # ishlamasdi — o'lchandi: streak 5 dan 1 ga tushardi.
        user.streak_count += 1
        user.streak_freeze_until = None
    else:
        user.streak_count = 1

    user.last_active_date = today
    user.save(update_fields=["streak_count", "last_active_date", "streak_freeze_until"])

    granted = quests.on_streak_reached(user, user.streak_count)
    return user.streak_count, granted


@transaction.atomic
def apply_freeze(user: User, days: int = 1) -> date:
    """Do'kondan sotib olingan streak freeze ni yoqadi.

    Freeze KELAJAKDAGI bo'shliqni yopadi: bugundan boshlab `days` kun
    ichida faol bo'lmasangiz ham streak uzilmaydi.
    """
    user = User.objects.select_for_update().get(pk=user.pk)
    base = max(user.streak_freeze_until or timezone.localdate(), timezone.localdate())
    user.streak_freeze_until = base + timedelta(days=days)
    user.save(update_fields=["streak_freeze_until"])
    return user.streak_freeze_until
