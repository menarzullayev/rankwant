"""Reyting manbai va audit — 05-domain-model 🔒."""

from __future__ import annotations

from typing import ClassVar

from django.db import models


class UserSolvedProblem(models.Model):
    """Skills manbai — faqat BIRINCHI AC.

    `difficulty_at_solve` audit uchun saqlanadi, lekin formulada
    ISHLATILMAYDI: Skills joriy qiyinlikdan hisoblanadi (ADR-0007).
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="solved")
    problem = models.ForeignKey(
        "problems.Problem", on_delete=models.CASCADE, related_name="solvers"
    )
    first_ac_at = models.DateTimeField(auto_now_add=True)
    first_ac_attempt = models.ForeignKey(
        "judging.Attempt", null=True, on_delete=models.SET_NULL, related_name="+"
    )
    difficulty_at_solve = models.PositiveIntegerField()

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="uniq_user_problem_solved")
        ]
        indexes: ClassVar = [
            models.Index(fields=["user"], name="solved_by_user"),
            # ADR-0007: qayta baholashda ta'sirlanganlarni topish uchun MAJBURIY
            models.Index(fields=["problem"], name="solved_by_problem"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} solved {self.problem_id}"


class RatingHistory(models.Model):
    """Har o'zgarishning SABABI — principle #2 ni texnik bajaradi."""

    class Type(models.TextChoices):
        SKILLS = "skills", "Skills"
        CONTEST = "contest", "Contests"
        ACTIVITY = "activity", "Activity"
        CHALLENGES = "challenges", "Challenges"

    class Reason(models.TextChoices):
        PROBLEM_SOLVED = "problem_solved", "Masala yechildi"
        PROBLEM_RERATED = "problem_rerated", "Masala qayta baholandi"
        CONTEST = "contest", "Musobaqa"
        RECALCULATION = "recalculation", "Qayta hisoblash"

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="rating_history")
    rating_type = models.CharField(max_length=16, choices=Type.choices)
    value_before = models.IntegerField()
    value_after = models.IntegerField()
    delta = models.IntegerField()
    reason = models.CharField(max_length=24, choices=Reason.choices)
    ref_type = models.CharField(max_length=24, blank=True)
    ref_id = models.CharField(max_length=64, blank=True)
    # Contest holatida Elo hisobini ko'rsatish uchun
    seed = models.FloatField(null=True, blank=True)
    rank = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["user", "rating_type", "-created_at"], name="rating_hist_feed")
        ]

    def __str__(self) -> str:
        return f"{self.user_id} {self.rating_type} {self.delta:+d} ({self.reason})"
