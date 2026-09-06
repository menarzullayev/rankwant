"""Celery tasklar — 08-technical-spec 🔒 § Reyting hisoblash."""

from __future__ import annotations

import logging

from celery import shared_task

from judging.provider import get_provider
from judging.services import apply_result

log = logging.getLogger(__name__)


@shared_task(name="judging.drain_results")
def drain_results(max_items: int = 100) -> int:
    """Judge natijalari navbatini bo'shatadi.

    Beat orqali tez-tez chaqiriladi. Har bir natija alohida tranzaksiyada
    yoziladi — bittasi yiqilsa qolganlari saqlanadi.
    """
    provider = get_provider()
    applied = 0
    for _ in range(max_items):
        result = provider.poll(timeout=1)
        if result is None:
            break
        try:
            if apply_result(result) is not None:
                applied += 1
        except Exception:
            log.exception("natijani yozib bo'lmadi: %s", result.get("job_id"))
    return applied
