"""Bildirishnoma yaratish. Chaqiruvchi kod xato bo'lsa ham yiqilmasligi kerak."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from core.models import User
from notifications import messages
from notifications.models import Notification

log = logging.getLogger(__name__)


#: Kanal standarti: sayt ichida — ha, Telegram — foydalanuvchi o'zi yoqadi.
#: Telegram'ga so'ramasdan xabar yuborish botni spamga aylantirardi.
DEFAULT_CHANNELS = {"site": True, "telegram": False}


def channels(user: User, kind: str) -> tuple[bool, bool]:
    """`(sayt, telegram)` — foydalanuvchining shu tur uchun tanlovi."""
    prefs = (user.notify_prefs or {}).get(kind) or {}
    return (
        bool(prefs.get("site", DEFAULT_CHANNELS["site"])),
        bool(prefs.get("telegram", DEFAULT_CHANNELS["telegram"])),
    )


def _telegram_text(title: str, body: str) -> str:
    from django.conf import settings

    parts = [title, body, f"{settings.SITE_URL}/notifications"]
    return "\n\n".join(p for p in parts if p)[:4000]


def _push_telegram(user: User, title: str, body: str) -> None:
    """Navbatga qo'yadi. Telegram ulanmagan bo'lsa jim o'tadi."""
    try:
        from core.models import SocialAccount
        from core.tasks import queue
        from notifications.tasks import send_telegram

        if SocialAccount.objects.filter(user=user, provider="telegram").exists():
            queue(send_telegram, user.pk, _telegram_text(title, body))
    except Exception:
        log.exception("telegram bildirishnomasi navbatga qo'yilmadi: %s", user.pk)


#: The stream event a new notification is announced with. The payload is
#: only a pointer: the client reads the row itself over REST (ADR-0029 —
#: the stream is an optimisation, never the source of truth).
EVENT_NOTIFICATION = "notification"

#: A bulk send announces itself to this many recipients at most. Beyond
#: that the rows are still written; their owners see them on the next
#: refresh. A post announced to every active user is ~974k rows — one
#: Redis round trip each would stall the task that sends it.
ANNOUNCE_MAX = 200


def compose(
    user: User,
    kind: str,
    title: str = "",
    *,
    body: str = "",
    code: str = "",
    params: dict[str, Any] | None = None,
    ref_type: str = "",
    ref_id: str | int = "",
) -> Notification:
    """An unsaved row. With a `code` the words come from the catalogue, in
    the recipient's language; `title`/`body` given explicitly win (free
    text a person wrote, such as a judge's feedback)."""
    if code:
        made_title, made_body = messages.render(code, params, user.locale)
        title = title or made_title
        body = body or made_body
    return Notification(
        user=user,
        kind=kind,
        title=title[:200],
        body=body,
        code=code,
        params=params or {},
        ref_type=ref_type,
        ref_id=str(ref_id),
    )


def announce(rows: Iterable[Notification]) -> None:
    """Tells open pages that these rows exist — after the transaction commits.

    Before the commit a subscriber would ask for a row it cannot see yet.
    A failed publish is swallowed inside `bus.publish`: the notification
    is in the database either way.
    """
    pointers = [(row.user_id, row.pk, row.kind) for row in rows if row.pk]
    if not pointers or len(pointers) > ANNOUNCE_MAX:
        return

    def publish() -> None:
        from realtime import bus

        for user_id, pk, kind in pointers:
            bus.publish(bus.user_channel(user_id), EVENT_NOTIFICATION, {"id": pk, "kind": kind})

    transaction.on_commit(publish)


def notify(
    user: User,
    kind: str,
    title: str = "",
    *,
    body: str = "",
    code: str = "",
    params: dict[str, Any] | None = None,
    ref_type: str = "",
    ref_id: str | int = "",
) -> Notification | None:
    """Bitta bildirishnoma — foydalanuvchi tanlagan kanallar bo'yicha.

    Xato yutiladi: bildirishnoma yiqilsa ham uni keltirib chiqargan amal
    (reyting, verdict) saqlanishi shart. Sayt kanali o'chirilgan bo'lsa
    `None` qaytadi — chaqiruvchi buni allaqachon ko'taradi.
    """
    site, telegram = channels(user, kind)
    try:
        draft = compose(
            user, kind, title, body=body, code=code, params=params, ref_type=ref_type, ref_id=ref_id
        )
    except Exception:
        log.exception("bildirishnoma tuzilmadi: %s / %s", user.pk, kind)
        return None
    row = None
    if site:
        try:
            draft.save()
            row = draft
            announce([row])
        except Exception:
            log.exception("bildirishnoma yaratilmadi: %s / %s", user.pk, kind)
    if telegram:
        _push_telegram(user, draft.title, draft.body)
    return row


def notify_many(
    users: Iterable[User],
    kind: str,
    title: str = "",
    *,
    body: str = "",
    code: str = "",
    params: dict[str, Any] | None = None,
    ref_type: str = "",
    ref_id: str | int = "",
) -> int:
    """Ko'p foydalanuvchiga bir xil xabar — bitta so'rovda.

    Faqat sayt kanali: ommaviy xabarni Telegram'ga birdaniga minglab
    yuborish bot chegarasiga urilardi.
    """
    rows = [
        compose(
            u, kind, title, body=body, code=code, params=params, ref_type=ref_type, ref_id=ref_id
        )
        for u in users
        if channels(u, kind)[0]
    ]
    if not rows:
        return 0
    try:
        created = Notification.objects.bulk_create(rows, batch_size=500)
    except Exception:
        log.exception("guruh bildirishnomasi yaratilmadi: %s", kind)
        return 0
    announce(created)
    return len(rows)


def mark_read(user: User, ids: list[int] | None = None) -> int:
    """Read implies seen: a row opened from a link never passed the bell."""
    qs = Notification.objects.filter(user=user, read_at__isnull=True)
    if ids is not None:
        qs = qs.filter(pk__in=ids)
    now = timezone.now()
    updated = qs.update(read_at=now)
    Notification.objects.filter(user=user, seen_at__isnull=True, read_at__isnull=False).update(
        seen_at=now
    )
    return updated


def mark_unread(user: User, ids: list[int]) -> int:
    """Back to unread. It stays seen — the bell does not ring for it again."""
    return Notification.objects.filter(user=user, pk__in=ids, read_at__isnull=False).update(
        read_at=None
    )


def mark_seen(user: User) -> int:
    """The bell was opened: everything listed so far has been seen."""
    return Notification.objects.filter(user=user, seen_at__isnull=True).update(
        seen_at=timezone.now()
    )


def clear_read(user: User) -> int:
    deleted, _ = Notification.objects.filter(user=user, read_at__isnull=False).delete()
    return deleted


def unread_count(user: User) -> int:
    return Notification.objects.filter(user=user, read_at__isnull=True).count()


def summary(user: User) -> dict[str, Any]:
    """What the bell and the page's tabs need, in two queries."""
    mine = Notification.objects.filter(user=user)
    counts = mine.aggregate(
        total=Count("pk"),
        unread=Count("pk", filter=Q(read_at__isnull=True)),
        unseen=Count("pk", filter=Q(read_at__isnull=True, seen_at__isnull=True)),
    )
    kinds = sorted(mine.order_by().values_list("kind", flat=True).distinct())
    return {**counts, "kinds": kinds}
