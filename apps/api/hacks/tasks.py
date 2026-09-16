"""Hack fazasining beat vazifalari — ADR-0020.

Ikkalasi ham musobaqa yakunlanishini BLOKDAN chiqaradi: `finalize_due`
hack fazasi yopilmaguncha reytingni qo'llamaydi, faza esa javobi
kelmagan hack turganda yopilmaydi.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from contests.models import Contest
from hacks.models import Hack
from hacks.services import abandon, close_hack_phase

log = logging.getLogger(__name__)

#: Hack shuncha vaqt qimirlamasa javob kelmaydi deb hisoblanadi.
#: Urinishnikidan (5 daqiqa) uzoqroq: hack uch bosqichdan o'tadi va har
#: biri navbatda kutishi mumkin.
STUCK_AFTER_MINUTES = 10

#: Bir yurishda shuncha hack yopiladi — qolgani keyingi chaqiruvda.
REAP_BATCH = 200


@shared_task(name="hacks.close_due")
def close_due() -> int:
    """Oynasi tugagan musobaqalarning hack fazasini yopadi.

    Yopish SHOSHILMAYDI: ochiq faza ketayotgan yoki javobi kelmagan hack
    bor musobaqa chetlab o'tiladi va keyingi chaqiruvda qayta ko'riladi.
    Aks holda hali tekshirilayotgan hack testi to'plamga tushmay qolib,
    reyting undan bexabar hisoblanardi.
    """
    now = timezone.now()
    due = Contest.objects.filter(end_at__lte=now, hack_phase_closed_at__isnull=True).exclude(
        hack_room=False, hack_open_minutes=0
    )
    closed = 0
    for contest in due:
        if contest.is_hack_open:
            continue
        if Hack.objects.filter(contest=contest, status=Hack.Status.TESTING).exists():
            continue
        try:
            close_hack_phase(contest)
        except Exception:
            log.exception("contest %s: hack fazasi yopilmadi", contest.slug)
            continue
        closed += 1
    return closed


@shared_task(name="hacks.reap_stuck")
def reap_stuck() -> int:
    """Javobi kelmagan hacklarni bo'shatadi.

    `judging.reap_stuck` urinishni qutqaradi, bu esa hackni: ikkalasi
    ham judge ish olib yiqilganda yo'qolgan javobning oqibati.
    """
    cutoff = timezone.now() - timedelta(minutes=STUCK_AFTER_MINUTES)
    stuck = Hack.objects.filter(status=Hack.Status.TESTING, updated_at__lt=cutoff)
    total = 0
    for hack in stuck.select_related("problem", "defender_attempt")[:REAP_BATCH]:
        try:
            abandon(hack, "judge javob bermadi — hack hisobga olinmadi")
        except Exception:
            log.exception("hack %s bo'shatilmadi", hack.pk)
            continue
        total += 1
    if total:
        log.warning("qotib qolgan hacklar: %s ta hisobga olinmadi", total)
    return total
