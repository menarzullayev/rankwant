"""Celery tasklar — 08-technical-spec 🔒 § Reyting hisoblash."""

from __future__ import annotations

import logging

from celery import shared_task

from judging.provider import get_provider
from judging.services import apply_custom_result, apply_result

log = logging.getLogger(__name__)


@shared_task(name="judging.drain_results")
def drain_results(max_items: int = 500) -> int:
    """Judge natijalari navbatini bo'shatadi.

    Beat orqali tez-tez chaqiriladi. Har bir natija alohida tranzaksiyada
    yoziladi — bittasi yiqilsa qolganlari saqlanadi.

    Shift ataylab keng: judge o'lchandi — 66 yechim/s, eski 100 talik
    chegara esa (2 s da, ikkita worker bilan) ~100/s berardi, ya'ni
    zaxira atigi 1.5 barobar edi. Navbat bo'sh bo'lsa sikl birinchi
    bo'sh o'qishda uziladi, ya'ni keng shift bo'sh turganda hech
    narsani qimmatlashtirmaydi.
    """
    provider = get_provider()
    applied = 0
    for _ in range(max_items):
        result = provider.poll(timeout=1)
        if result is None:
            break
        try:
            handled = (
                apply_custom_result(result) if result.get("custom_run_id") else apply_result(result)
            )
            if handled is not None:
                applied += 1
        except Exception:
            log.exception("natijani yozib bo'lmadi: %s", result.get("job_id"))
    return applied
