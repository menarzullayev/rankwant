"""Telegram orqali bildirishnoma — @rankwantbot."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any

from celery import shared_task
from django.conf import settings

from core.http_retry import open_with_retry

log = logging.getLogger(__name__)


def _post(url: str, payload: dict[str, Any]) -> int:
    """JSON yuboradi va HTTP holat kodini qaytaradi. Tarmoq xatosi — `OSError`."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        # `label` ataylab umumiy: URL ichida bot tokeni bor, u log'ga
        # tushmasligi kerak.
        with open_with_retry(request, timeout=10, label="telegram") as resp:
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return exc.code


@shared_task(name="notifications.send_telegram")
def send_telegram(user_id: int, text: str) -> str:
    """Botdan foydalanuvchiga xabar.

    Bot odamga faqat u ruxsat bergan bo'lsa yoza oladi — Telegram
    vidjeti buni `request_access=write` bilan so'raydi. Ruxsat yo'q yoki
    bot bloklangan bo'lsa Telegram 403 qaytaradi: bu xato emas, holat.

    Token hech qayerda yozilmaydi — URL ichida bo'lgani uchun so'rov
    manzili ham, xato matni ham log'ga tushmaydi.
    """
    from core.models import SocialAccount

    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return "skipped"
    account = SocialAccount.objects.filter(user_id=user_id, provider="telegram").first()
    if account is None or not account.uid.isdigit():
        return "skipped"
    try:
        status = _post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            {"chat_id": int(account.uid), "text": text, "disable_web_page_preview": True},
        )
    except OSError:
        log.warning("telegram xabari yuborilmadi (tarmoq): %s", user_id)
        return "failed"
    if status != 200:
        log.info("telegram xabari qabul qilinmadi: %s → %s", user_id, status)
        return f"failed:{status}"
    return "sent"


@shared_task(name="notifications.send_email")
def send_notification_email(
    *, user_id: int, kind: str, title: str, body: str, notification_id: int | None = None
) -> str:
    """Email copy of a notification, five minutes after it (`notifications.email`).

    Everything is checked again here, not when it was queued: the reader may
    have read the row, switched the kind off or lost the verified address
    in the meantime, and the day's quota is what it is now.
    """
    from notifications.email import deliver

    return deliver(
        user_id=user_id, kind=kind, title=title, body=body, notification_id=notification_id
    )
