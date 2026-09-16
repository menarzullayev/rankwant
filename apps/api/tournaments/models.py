"""Chempionat — bir nechta musobaqadan iborat seriya.

Har bosqich oddiy Contest: judge, standings, reyting o'zgarmaydi.
Chempionat faqat bosqich natijalarini bitta jadvalga yig'adi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.mixins import TimeWindowMixin


class Tournament(TimeWindowMixin, models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Markdown")
    start_at = models.DateTimeField(db_index=True)
    end_at = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-start_at"]

    def __str__(self) -> str:
        return self.slug


class TournamentStage(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="stages")
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=120)
    contest = models.OneToOneField(
        "contests.Contest", on_delete=models.PROTECT, related_name="tournament_stage"
    )
    #: Final bosqichi ko'proq ball bersin desa — koeffitsient
    weight = models.PositiveIntegerField(default=1)

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["tournament", "order"], name="uniq_stage_order")
        ]

    def __str__(self) -> str:
        return f"{self.tournament_id}#{self.order}"


class TournamentStanding(models.Model):
    """Yig'ma jadval — `services.rebuild` qayta hisoblaydi."""

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="standings")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="+")
    rank = models.PositiveIntegerField()
    points = models.PositiveIntegerField(default=0)
    solved_total = models.PositiveIntegerField(default=0)
    stages_played = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["rank"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["tournament", "user"], name="uniq_tournament_standing")
        ]

    def __str__(self) -> str:
        return f"{self.tournament_id} {self.user_id} #{self.rank}"
