"""O'qituvchi sinfi — PRD P2-2.

B2B yo'nalishining texnik asosi: o'qituvchi sinf yaratadi, o'quvchilarni
qo'shadi, uy vazifasi beradi va progressni ko'radi.

Bu RoboContest «Judge rejasi» ga javob (03-market-research).
"""

from __future__ import annotations

import secrets
from typing import ClassVar

from django.db import models


class Classroom(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=120)
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="owned_classrooms"
    )
    description = models.TextField(blank=True)
    #: Qo'shilish kodi — havola bilan tarqatiladi
    join_code = models.CharField(max_length=12, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    MAX_MEMBERS = 200

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.join_code:
            self.join_code = secrets.token_urlsafe(6)[:12]
        super().save(*args, **kwargs)  # type: ignore[arg-type]


class ClassroomMember(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "O'quvchi"
        ASSISTANT = "assistant", "Yordamchi"

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="classroom_memberships"
    )
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.STUDENT)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["joined_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["classroom", "user"], name="uniq_classroom_member")
        ]

    def __str__(self) -> str:
        return f"{self.classroom_id} — {self.user_id}"


class Assignment(models.Model):
    """Uy vazifasi — sinfga berilgan masalalar to'plami."""

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    problems = models.ManyToManyField("problems.Problem", related_name="assignments")
    due_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.classroom_id}: {self.title}"
