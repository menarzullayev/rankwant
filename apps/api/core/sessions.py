"""Kirilgan qurilmalar — ro'yxat va uzish.

Haqiqat manbai Django sessiyasi; `UserSession` unga faqat ko'rinish
beradi. Sessiya muddati tugagan yoki chiqilgan qatorlar ro'yxat
so'ralganda tozalanadi.
"""

from __future__ import annotations

from datetime import datetime
from importlib import import_module
from typing import Any

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Max
from django.utils import timezone

from core.models import User, UserSession

#: `last_seen` ni har so'rovda yozish har sahifa ochilishini bazaga
#: yozishga aylanardi. Besh daqiqa — «hozir» va «kecha» ni ajratishga yetadi.
TOUCH_EVERY = 300
#: «Onlayn» oynasi: `last_seen` har besh daqiqada yoziladi — ikki barobar
#: zaxira sahifani o'qib o'tirgan odamni o'chib-yonishdan saqlaydi.
ONLINE_WINDOW = 2 * TOUCH_EVERY


def _store(key: str) -> Any:
    return import_module(settings.SESSION_ENGINE).SessionStore(session_key=key)


def record(request: Any, *, force: bool = False) -> None:
    user = getattr(request, "user", None)
    session = getattr(request, "session", None)
    key = session.session_key if session is not None else None
    if user is None or not user.is_authenticated or not key:
        return
    mark = f"sess:touch:{key}"
    if not force and cache.get(mark):
        return
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = (forwarded.split(",")[0].strip() if forwarded else "") or request.META.get("REMOTE_ADDR")
    UserSession.objects.update_or_create(
        session_key=key,
        defaults={
            "user": user,
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:200],
            "ip": ip or None,
            "last_seen": timezone.now(),
        },
    )
    cache.set(mark, 1, TOUCH_EVERY)


def live(user: User) -> list[UserSession]:
    rows = list(UserSession.objects.filter(user=user))
    alive = set(
        Session.objects.filter(
            session_key__in=[r.session_key for r in rows], expire_date__gt=timezone.now()
        ).values_list("session_key", flat=True)
    )
    dead = [r.pk for r in rows if r.session_key not in alive]
    if dead:
        UserSession.objects.filter(pk__in=dead).delete()
    return [r for r in rows if r.session_key in alive]


def terminate(row: UserSession) -> None:
    _store(row.session_key).delete()
    row.delete()


def terminate_others(user: User, *, keep: str | None) -> int:
    rows = list(UserSession.objects.filter(user=user).exclude(session_key=keep or ""))
    for row in rows:
        terminate(row)
    return len(rows)


def last_seen(user: User) -> datetime | None:
    """Oxirgi faollik — hamma qurilmalar bo'yicha."""
    value: datetime | None = UserSession.objects.filter(user=user).aggregate(last=Max("last_seen"))[
        "last"
    ]
    return value
