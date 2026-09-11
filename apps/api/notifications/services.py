"""Bildirishnoma yaratish. Chaqiruvchi kod xato bo'lsa ham yiqilmasligi kerak."""

from __future__ import annotations

import logging
from collections.abc import Iterable

from django.utils import timezone

from core.models import User
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


def notify(
    user: User,
    kind: str,
    title: str,
    *,
    body: str = "",
    ref_type: str = "",
    ref_id: str = "",
) -> Notification | None:
    """Bitta bildirishnoma — foydalanuvchi tanlagan kanallar bo'yicha.

    Xato yutiladi: bildirishnoma yiqilsa ham uni keltirib chiqargan amal
    (reyting, verdict) saqlanishi shart. Sayt kanali o'chirilgan bo'lsa
    `None` qaytadi — chaqiruvchi buni allaqachon ko'taradi.
    """
    site, telegram = channels(user, kind)
    row = None
    if site:
        try:
            row = Notification.objects.create(
                user=user,
                kind=kind,
                title=title,
                body=body,
                ref_type=ref_type,
                ref_id=str(ref_id),
            )
        except Exception:
            log.exception("bildirishnoma yaratilmadi: %s / %s", user.pk, kind)
    if telegram:
        _push_telegram(user, title, body)
    return row


def notify_many(
    users: Iterable[User],
    kind: str,
    title: str,
    *,
    body: str = "",
    ref_type: str = "",
    ref_id: str = "",
) -> int:
    """Ko'p foydalanuvchiga bir xil xabar — bitta so'rovda.

    Faqat sayt kanali: ommaviy xabarni Telegram'ga birdaniga minglab
    yuborish bot chegarasiga urilardi.
    """
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
        if channels(u, kind)[0]
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
