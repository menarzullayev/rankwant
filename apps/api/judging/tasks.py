"""Celery tasklar — 08-technical-spec 🔒 § Reyting hisoblash."""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task

from judging.provider import get_provider
from judging.services import apply_custom_result, apply_result

log = logging.getLogger(__name__)

#: Urinish shuncha turgach qotib qolgan deb hisoblanadi. Judge odatda
#: soniyalarda javob beradi, lekin gavjum musobaqada navbat chuqur
#: bo'ladi — chegara shuni hisobga oladi.
STUCK_AFTER_MINUTES = 5


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


@shared_task(name="judging.reap_stuck")
def reap_stuck() -> dict[str, int]:
    """Verdikt kelmagan urinishlarni qutqaradi.

    Judge navbatdan ishni oladi va shundan keyin yiqilsa (deploy, OOM),
    ish yo'qoladi: navbatda ham yo'q, natija ham kelmaydi. Urinish esa
    abadiy «tekshirilmoqda» bo'lib qolardi va foydalanuvchi hech qachon
    javob ko'rmasdi.

    Bir marta qayta navbatga qo'yiladi — judge shunchaki sekin bo'lgan
    bo'lishi mumkin. Qayta urinish ham qotsa, IE qo'yiladi: yolg'on
    kutishdan ko'ra halol xato yaxshi.
    """
    from django.utils import timezone

    from judging.models import Attempt
    from judging.services import build_job
    from judging.verdicts import Verdict

    cutoff = timezone.now() - timedelta(minutes=STUCK_AFTER_MINUTES)
    pending = Attempt.objects.filter(verdict__in=[Verdict.PENDING, Verdict.RUNNING])

    provider = get_provider()
    requeued = 0
    for attempt in pending.filter(requeued_at__isnull=True, created_at__lt=cutoff).select_related(
        "problem", "language"
    )[:200]:
        try:
            provider.submit(build_job(attempt))
        except Exception:
            log.exception("qayta navbatga qo'yib bo'lmadi: %s", attempt.pk)
            continue
        Attempt.objects.filter(pk=attempt.pk).update(requeued_at=timezone.now())
        requeued += 1

    failed = pending.filter(requeued_at__lt=cutoff).update(
        verdict=Verdict.IE, judged_at=timezone.now()
    )
    if requeued or failed:
        log.warning("qotib qolgan urinishlar: %s qayta, %s IE", requeued, failed)
    return {"requeued": requeued, "failed": failed}
