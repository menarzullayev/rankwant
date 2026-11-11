"""Coach and student (ADR-0061 § 4).

A coach is someone a student chose and who accepted: not the owner of a
classroom the student sits in — that person is the student's *teacher*
(ADR-0017 used "coach" for both until 2026-11-11).
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.bases import CreatedModel


class CoachLink(CreatedModel):
    """One student and one coach. The student asks, the coach answers.

    `can_view_attempts` is the student's consent for THIS coach to open their
    solutions; a new link takes it from `User.coach_can_view_attempts`.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        ACTIVE = "active", "Faol"
        REJECTED = "rejected", "Rad etildi"
        ENDED = "ended", "Tugatildi"

    student = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="coach_links")
    coach = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="coached_links")
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    can_view_attempts = models.BooleanField(default=False)
    decided_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["student", "coach"], name="uniq_coach_link"),
            models.CheckConstraint(
                condition=~models.Q(student=models.F("coach")), name="coach_is_not_self"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.coach_id} → {self.student_id} ({self.status})"


class Recommendation(CreatedModel):
    """A problem a coach suggests; it shows in the student's tasks."""

    link = models.ForeignKey(CoachLink, on_delete=models.CASCADE, related_name="recommendations")
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="+")
    note = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["link", "problem"], name="uniq_coach_recommendation")
        ]
