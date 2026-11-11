"""O'qituvchi sinfi — PRD P2-2.

B2B yo'nalishining texnik asosi: o'qituvchi sinf yaratadi, o'quvchilarni
qo'shadi, uy vazifasi beradi va progressni ko'radi.

Bu RoboContest «Judge rejasi» ga javob (03-market-research).
"""

from __future__ import annotations

import secrets
from typing import ClassVar

from django.db import models

from core.bases import CreatedModel


class Classroom(CreatedModel):
    class JoinMode(models.TextChoices):
        #: The code is enough: the student is a member at once.
        INSTANT = "instant", "Darhol"
        #: The code sends a request the teacher approves (ADR-0061 § 3).
        APPROVAL = "approval", "Tasdiq bilan"

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=120)
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="owned_classrooms"
    )
    description = models.TextField(blank=True)
    #: Qo'shilish kodi — havola bilan tarqatiladi
    join_code = models.CharField(max_length=12, unique=True, db_index=True)
    #: A new classroom asks for approval; the migration left the classrooms
    #: that existed before ADR-0061 instant, as they worked.
    join_mode = models.CharField(max_length=12, choices=JoinMode.choices, default=JoinMode.APPROVAL)
    #: `False` — archived. A classroom is never deleted through the API:
    #: its assignments and reports stay readable to staff.
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.join_code:
            self.join_code = new_code()
        super().save(*args, **kwargs)  # type: ignore[arg-type]


def new_code() -> str:
    """A join code: eight URL-safe characters, unique enough to retry once."""
    return secrets.token_urlsafe(6)[:12]


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


class ClassroomJoinRequest(CreatedModel):
    """A student's request to join a classroom that asks for approval.

    Not a `ClassroomMember` row: creating a member enrols the student in the
    class's free courses (ADR-0056 § 8), which must wait for the teacher.
    One row per (classroom, user); asking again after a rejection reopens it.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        APPROVED = "approved", "Qabul qilindi"
        REJECTED = "rejected", "Rad etildi"

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="requests")
    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="classroom_requests"
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    class Meta:
        ordering: ClassVar = ["created_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["classroom", "user"], name="uniq_classroom_request")
        ]

    def __str__(self) -> str:
        return f"{self.classroom_id} — {self.user_id} ({self.status})"


class Assignment(CreatedModel):
    """Uy vazifasi — sinfga berilgan masalalar to'plami va/yoki kurs."""

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    problems = models.ManyToManyField("problems.Problem", related_name="assignments")
    #: A course given to the class (ADR-0056 part 8). A free course enrols
    #: every student; a Qvant or paid one is unlocked by each student.
    course = models.ForeignKey(
        "courses.Course",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="classroom_assignments",
    )
    #: A quiz given to the class (ADR-0061 § 5): the teacher's own or a
    #: public one.
    quiz = models.ForeignKey(
        "quizzes.Quiz",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="classroom_assignments",
    )
    due_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.classroom_id}: {self.title}"
