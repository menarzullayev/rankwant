"""Chempionat yig'ma jadvali.

Ball formulasi OCHIQ (principle #2): har bosqichda
    ball = weight × (ishtirokchilar − o'rin + 1)
Ya'ni birinchi o'rin bosqichdagi odamlar sonicha ball oladi, oxirgi — 1.
Bosqichlar turli o'lchamda bo'lsa ham solishtirish mumkin. Tenglikda
umumiy yechilgan masalalar soni hal qiladi.
"""

from __future__ import annotations

from collections import defaultdict

from django.db import transaction

from contests.models import Standing
from tournaments.models import Tournament, TournamentStanding


def stage_points(weight: int, participants: int, rank: int) -> int:
    return weight * max(0, participants - rank + 1)


@transaction.atomic
def rebuild(tournament: Tournament) -> int:
    # Qulf: quyidagi DELETE + `bulk_create` juftligi qulfsiz bo'lsa,
    # ustma-ust tushgan ikkinchi qayta qurish birinchisining yozgan
    # qatorlarini o'z DELETE ida KO'RMAYDI (READ COMMITTED) va
    # `uniq_tournament_standing` ga uriladi. Ma'lumot buzilmaydi —
    # tranzaksiya orqaga qaytadi — lekin chaqiruvchi 500 oladi.
    # O'lchandi: 8 parallel chaqiruvdan 7 tasi IntegrityError bergan.
    tournament = Tournament.objects.select_for_update().get(pk=tournament.pk)

    points: dict[int, int] = defaultdict(int)
    solved: dict[int, int] = defaultdict(int)
    played: dict[int, int] = defaultdict(int)

    for stage in tournament.stages.select_related("contest"):
        rows = list(Standing.objects.filter(contest=stage.contest).order_by("rank"))
        n = len(rows)
        for row in rows:
            points[row.user_id] += stage_points(stage.weight, n, row.rank)
            solved[row.user_id] += row.solved_count
            played[row.user_id] += 1

    ordered = sorted(points, key=lambda uid: (-points[uid], -solved[uid], uid))
    TournamentStanding.objects.filter(tournament=tournament).delete()
    TournamentStanding.objects.bulk_create(
        [
            TournamentStanding(
                tournament=tournament,
                user_id=uid,
                rank=i + 1,
                points=points[uid],
                solved_total=solved[uid],
                stages_played=played[uid],
            )
            for i, uid in enumerate(ordered)
        ]
    )
    return len(ordered)


def rebuild_for_contest(contest_id: int) -> None:
    """Contest yakunlangach — u biror bosqich bo'lsa chempionat jadvali yangilanadi."""
    from tournaments.models import TournamentStage

    stage = (
        TournamentStage.objects.filter(contest_id=contest_id).select_related("tournament").first()
    )
    if stage is not None:
        rebuild(stage.tournament)
