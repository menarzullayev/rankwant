"""Telegram orqali bildirishnoma — @rankwantbot."""

from __future__ import annotations

import logging

import requests
from celery import shared_task
from django.conf import settings

log = logging.getLogger(__name__)


@shared_task(name="notifications.send_telegram")
def send_telegram(user_id: int, text: str) -> str:
    """Botdan foydalanuvchiga xabar.

    Bot odamga faqat u ruxsat bergan bo'lsa yoza oladi — Telegram
    vidjeti buni `request_access=write` bilan so'raydi. Ruxsat yo'q yoki
    bot bloklangan bo'lsa Telegram 403 qaytaradi: bu xato emas, holat.

    Token hech qayerda yozilmaydi — URL ichida bo'lgani uchun so'rov
    manzili ham log'ga tushmaydi.
    """
    from core.models import SocialAccount

    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return "skipped"
    account = SocialAccount.objects.filter(user_id=user_id, provider="telegram").first()
    if account is None or not account.uid.isdigit():
        return "skipped"
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": int(account.uid), "text": text, "disable_web_page_preview": True},
            timeout=10,
        )
    except requests.RequestException:
        log.warning("telegram xabari yuborilmadi (tarmoq): %s", user_id)
        return "failed"
    if resp.status_code != 200:
        log.info("telegram xabari qabul qilinmadi: %s → %s", user_id, resp.status_code)
        return f"failed:{resp.status_code}"
    return "sent"
