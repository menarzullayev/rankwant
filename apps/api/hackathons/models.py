"""Hakaton — loyiha topshiriladi, judge emas, odam baholaydi.

Reytingga ta'sir qilmaydi (04-prd: reyting faqat masala va musobaqadan).
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils import timezone

from core.mixins import TimeWindowMixin


class Hackathon(TimeWindowMixin, models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Markdown: shartlar, mezonlar, sovrin")
    start_at = models.DateTimeField(db_index=True)
    #: Shu vaqtdan keyin topshirish yopiladi va barcha loyihalar ochiq ko'rinadi
    submission_deadline = models.DateTimeField()
    end_at = models.DateTimeField(help_text="Natijalar e'lon qilinadigan vaqt")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-start_at"]

    def __str__(self) -> str:
        return self.slug

    @property
    def accepts_submissions(self) -> bool:
        return self.start_at <= timezone.now() < self.submission_deadline


class HackathonSubmission(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="hackathon_entries"
    )
    team_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Markdown")
    repo_url = models.URLField()
    demo_url = models.URLField(blank=True)
    submitted_at = models.DateTimeField(auto_now=True)

    score = models.PositiveIntegerField(null=True, blank=True, help_text="0–100")
    feedback = models.TextField(blank=True)
    scored_by = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    scored_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-score", "submitted_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["hackathon", "user"], name="uniq_hackathon_entry")
        ]

    def __str__(self) -> str:
        return f"{self.hackathon_id} {self.user_id}: {self.title}"
