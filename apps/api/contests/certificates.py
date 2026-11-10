"""Sertifikat berish (ADR-0019).

Rasmiy musobaqa — ommaviy va virtual emas. Sertifikat kamida bitta yechim
yuborgan har ishtirokchiga beriladi: standings faqat musobaqa oynasidagi
urinishlardan quriladi, ya'ni virtual ishtirok bu yerga kirmaydi.
"""

from __future__ import annotations

import math

from contests.models import Certificate, Contest, Standing
from judging.models import Attempt

#: Shu ulushgacha bo'lganlar «eng yaxshi 10%» dizaynini oladi.
TOP_SHARE = 0.10


def issue(contest: Contest) -> int:
    """Musobaqa yakunlangach. Takroriy chaqiruv xavfsiz — bor sertifikat id'si saqlanadi."""
    if not contest.is_public or contest.is_virtual:
        return 0
    submitted = set(
        Attempt.objects.filter(contest=contest, created_at__lt=contest.end_at)
        .values_list("user_id", flat=True)
        .distinct()
    )
    rows = [
        row
        # An insider took part unrated: no place, no certificate (ADR-0055).
        for row in Standing.objects.filter(contest=contest)
        .official()
        .select_related("user")
        .order_by("rank")
        if row.user_id in submitted and row.user.is_active
    ]
    if not rows:
        return 0
    ioi = contest.scoring_type == Contest.Scoring.IOI

    def result(row: Standing) -> tuple[int, ...]:
        return (row.total_score,) if ioi else (row.solved_count, row.penalty)

    # `Standing.rank` ketma-ket — teng natija bir o'rinni bo'lishadi (33–35 → 33).
    place: dict[tuple[int, ...], int] = {}
    for row in rows:
        place.setdefault(result(row), row.rank)
    top = math.ceil(len(rows) * TOP_SHARE)
    medals = {1: Certificate.Tier.GOLD, 2: Certificate.Tier.SILVER, 3: Certificate.Tier.BRONZE}
    certificates = []
    for row in rows:
        at = place[result(row)]
        scored = result(row)[0] > 0
        tier = (
            medals[at]
            if scored and at in medals
            else Certificate.Tier.TOP10
            if scored and at <= top
            else Certificate.Tier.PARTICIPANT
        )
        certificates.append(
            Certificate(
                user=row.user,
                contest=contest,
                name=row.user.display_name or row.user.username,
                place=at,
                participants=len(rows),
                tier=tier,
            )
        )
    # A certificate already issued keeps its id (its QR link) and takes the
    # current place: a disqualification moves the places (ADR-0055, part 4).
    existing = {c.user_id: c for c in Certificate.objects.filter(contest=contest)}
    changed = []
    for cert in certificates:
        held = existing.get(cert.user_id)
        if held is not None and (held.place, held.participants, held.tier) != (
            cert.place,
            cert.participants,
            cert.tier,
        ):
            held.place, held.participants, held.tier = cert.place, cert.participants, cert.tier
            changed.append(held)
    Certificate.objects.bulk_update(changed, ["place", "participants", "tier"])
    Certificate.objects.bulk_create(
        [c for c in certificates if c.user_id not in existing], ignore_conflicts=True
    )
    return len(certificates)
