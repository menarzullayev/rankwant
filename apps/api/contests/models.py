"""Musobaqa — 05-domain-model 🔒."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import ClassVar

from django.db import models
from django.utils import timezone


class Contest(models.Model):
    class Scoring(models.TextChoices):
        ACM = "acm", "ACM/ICPC"
        IOI = "ioi", "IOI"

    slug = models.SlugField(unique=True, max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    freeze_minutes = models.PositiveIntegerField(
        default=0, help_text="Oxirgi N daqiqada standings muzlatiladi"
    )
    scoring_type = models.CharField(max_length=8, choices=Scoring.choices, default=Scoring.ACM)

    # Contests reytingi FAQAT shunga tayanadi (ADR-0006)
    is_rated = models.BooleanField(default=False)
    is_virtual = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    mirror_of = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="mirrors"
    )
    ratings_applied_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-start_at"]

    def __str__(self) -> str:
        return self.slug

    @property
    def is_running(self) -> bool:
        return self.start_at <= timezone.now() < self.end_at

    @property
    def is_finished(self) -> bool:
        return timezone.now() >= self.end_at

    @property
    def freeze_at(self) -> datetime | None:
        """Muzlatish boshlanadigan payt — yo'q bo'lsa None."""
        if not self.freeze_minutes:
            return None
        return self.end_at - timedelta(minutes=self.freeze_minutes)

    @property
    def is_frozen(self) -> bool:
        """Oxirgi `freeze_minutes` — standings yangilanishi to'xtaydi."""
        frozen_from = self.freeze_at
        return bool(frozen_from and self.is_running and timezone.now() >= frozen_from)


class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="problems")
    problem = models.ForeignKey(
        "problems.Problem", on_delete=models.PROTECT, related_name="contest_entries"
    )
    index_letter = models.CharField(max_length=3)
    points = models.PositiveIntegerField(default=100)

    class Meta:
        ordering: ClassVar = ["index_letter"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "index_letter"], name="uniq_contest_index"),
            models.UniqueConstraint(fields=["contest", "problem"], name="uniq_contest_problem"),
        ]

    def __str__(self) -> str:
        return f"{self.contest.slug}/{self.index_letter}"


class ContestRegistration(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="contest_registrations"
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    virtual_start_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "user"], name="uniq_contest_registration")
        ]

    def __str__(self) -> str:
        return f"{self.contest_id}/{self.user_id}"


class Standing(models.Model):
    """MATERIALLASHTIRILGAN — live hisoblash 500 parallel submit ostida
    standings so'rovini buzadi (04-prd NFR)."""

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="standings")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="standings")
    rank = models.PositiveIntegerField(default=0)
    solved_count = models.PositiveIntegerField(default=0)
    penalty = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    last_ac_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["rank"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "user"], name="uniq_contest_standing")
        ]
        indexes: ClassVar = [models.Index(fields=["contest", "rank"], name="standing_board")]

    def __str__(self) -> str:
        return f"{self.contest.slug} #{self.rank} {self.user_id}"
