"""Bildirishnoma yaratish. Chaqiruvchi kod xato bo'lsa ham yiqilmasligi kerak."""

from __future__ import annotations

import logging
from collections.abc import Iterable

from django.utils import timezone

from core.models import User
from notifications.models import Notification

log = logging.getLogger(__name__)


def notify(
    user: User,
    kind: str,
    title: str,
    *,
    body: str = "",
    ref_type: str = "",
    ref_id: str = "",
) -> Notification | None:
    """Bitta bildirishnoma. Xato yutiladi: bildirishnoma yiqilsa ham
    uni keltirib chiqargan amal (reyting, verdict) saqlanishi shart."""
    try:
        return Notification.objects.create(
            user=user,
            kind=kind,
            title=title,
            body=body,
            ref_type=ref_type,
            ref_id=str(ref_id),
        )
    except Exception:
        log.exception("bildirishnoma yaratilmadi: %s / %s", user.pk, kind)
        return None


def notify_many(
    users: Iterable[User],
    kind: str,
    title: str,
    *,
    body: str = "",
    ref_type: str = "",
    ref_id: str = "",
) -> int:
    """Ko'p foydalanuvchiga bir xil xabar — bitta so'rovda."""
    rows = [
        Notification(
            user=u,
            kind=kind,
            title=title,
            body=body,
            ref_type=ref_type,
            ref_id=str(ref_id),
        )
        for u in users
    ]
    if not rows:
        return 0
    try:
        Notification.objects.bulk_create(rows, batch_size=500)
    except Exception:
        log.exception("guruh bildirishnomasi yaratilmadi: %s", kind)
        return 0
    return len(rows)


def mark_read(user: User, ids: list[int] | None = None) -> int:
    qs = Notification.objects.filter(user=user, read_at__isnull=True)
    if ids is not None:
        qs = qs.filter(pk__in=ids)
    return qs.update(read_at=timezone.now())


def unread_count(user: User) -> int:
    return Notification.objects.filter(user=user, read_at__isnull=True).count()
