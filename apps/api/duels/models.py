"""Duel — 1v1 kod bellashuvi (PRD Phase 3, Challenges reytingi).

Chaqiriq tashlanadi → kimdir qabul qiladi → belgilangan vaqtda ikkalasi
bir xil masalalarni yechadi → g'olib Elo oladi (`formulas.duel_delta`).

Natija Attempt jadvalidan hisoblanadi: ikki o'yinchining duel
masalalariga VAQT ORALIG'IDAGI AC'lari. Attempt modeliga alohida
`duel` maydoni qo'shilmaydi — submit oqimi o'zgarmaydi.
"""

from __future__ import annotations

import secrets
from typing import ClassVar

from django.db import models
from django.utils import timezone


class Duel(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Kutilmoqda"
        ACCEPTED = "accepted", "Qabul qilindi"
        FINISHED = "finished", "Tugadi"
        CANCELLED = "cancelled", "Bekor qilindi"

    slug = models.SlugField(unique=True, max_length=16)
    title = models.CharField(max_length=120)
    challenger = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="duels_challenged"
    )
    opponent = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.CASCADE, related_name="duels_accepted"
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.OPEN, db_index=True
    )

    problem_count = models.PositiveIntegerField(default=4)
    #: Masalalar shu qiyinlik atrofidan tanlanadi (±DIFFICULTY_WINDOW)
    difficulty = models.PositiveIntegerField(default=1200)
    duration_minutes = models.PositiveIntegerField(default=60)
    start_at = models.DateTimeField(db_index=True)
    problems = models.ManyToManyField("problems.Problem", through="DuelProblem")

    winner = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="duels_won"
    )
    challenger_solved = models.PositiveIntegerField(default=0)
    opponent_solved = models.PositiveIntegerField(default=0)
    is_draw = models.BooleanField(default=False)
    ratings_applied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return self.slug

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = secrets.token_urlsafe(6)[:10].lower().replace("_", "x").replace("-", "y")
        super().save(*args, **kwargs)  # type: ignore[arg-type]

    @property
    def end_at(self):  # type: ignore[no-untyped-def]
        from datetime import timedelta

        return self.start_at + timedelta(minutes=self.duration_minutes)

    @property
    def is_running(self) -> bool:
        return self.status == self.Status.ACCEPTED and self.start_at <= timezone.now() < self.end_at

    @property
    def is_due(self) -> bool:
        return self.status == self.Status.ACCEPTED and timezone.now() >= self.end_at

    def participants(self) -> list:  # type: ignore[type-arg]
        return [u for u in (self.challenger, self.opponent) if u is not None]


class DuelProblem(models.Model):
    duel = models.ForeignKey(Duel, on_delete=models.CASCADE, related_name="items")
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="+")
    order = models.PositiveIntegerField()

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["duel", "order"], name="uniq_duel_problem_order"),
            models.UniqueConstraint(fields=["duel", "problem"], name="uniq_duel_problem"),
        ]

    def __str__(self) -> str:
        return f"{self.duel_id}#{self.order}"
