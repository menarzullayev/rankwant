"""AI tutor conversations (ADR-0065).

One conversation per student and problem: the side panel continues where
it stopped. The student's own words and code live here for 90 days
(decision ⑦) and the student may delete them at any time. This app is not
registered in the Django admin: staff see a conversation only when it is
reported (a later change).
"""

from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.db import models

from core.bases import CreatedModel, TimeStampedModel, UpdatedModel


class Conversation(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_conversations"
    )
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="+")
    #: The highest hint step given so far (0 — none); the ladder climbs one step at a time.
    hint_level = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="tutor_one_per_problem")
        ]
        indexes: ClassVar = [models.Index(fields=["updated_at"], name="tutor_conv_updated")]

    def __str__(self) -> str:
        return f"{self.user_id}/{self.problem_id}"


class Message(CreatedModel):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TUTOR = "tutor", "Tutor"

    class Kind(models.TextChoices):
        ASK = "ask", "Savol"
        HINT = "hint", "Maslahat"
        WHY_WRONG = "why_wrong", "Nega xato?"

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        DONE = "done", "Tayyor"
        FAILED = "failed", "Xato"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    #: Repeated from the conversation so the daily count is one indexed query.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    role = models.CharField(max_length=8, choices=Role.choices)
    kind = models.CharField(max_length=12, choices=Kind.choices)
    #: A tutor reply points at the student message it answers.
    reply_to = models.OneToOneField(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="reply"
    )
    text = models.TextField(blank=True)
    hint_level = models.PositiveSmallIntegerField(null=True, blank=True)
    #: «Nega xato?»: the attempt it is about.
    attempt = models.ForeignKey(
        "judging.Attempt", on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    #: Code the student attached to a question (the attempt's code is not copied).
    code = models.TextField(blank=True)
    code_language = models.CharField(max_length=64, blank=True)
    locale = models.CharField(max_length=3, default="uz")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.DONE)
    #: Why a reply failed: `timeout`, `busy`, `unavailable`, `ai_off_in_contest` …
    error = models.CharField(max_length=32, blank=True)
    model = models.CharField(max_length=64, blank=True)
    provider = models.CharField(max_length=16, blank=True)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    cache_read_tokens = models.PositiveIntegerField(default=0)
    cache_write_tokens = models.PositiveIntegerField(default=0)
    #: What the reply would cost on the API — the monthly budget sums it (decision ⑧).
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    #: Long code blocks the guard cut from the reply (ADR-0065 § 2.4).
    code_removed = models.PositiveSmallIntegerField(default=0)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["created_at", "pk"]
        indexes: ClassVar = [
            models.Index(fields=["user", "role", "created_at"], name="tutor_msg_daily"),
            models.Index(fields=["status", "created_at"], name="tutor_msg_pending"),
        ]

    def __str__(self) -> str:
        return f"{self.role}:{self.kind}:{self.pk}"


class DailyUse(models.Model):
    """Replies a student got on one day (decision ③).

    A counter of its own, not a count of messages: the student may delete a
    conversation (decision ⑦), and deleting must not hand the day's
    allowance back (measured 2026-11-12: it did, while the count was taken
    from the messages). Holds no content — only a number per day.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    day = models.DateField()
    count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "day"], name="tutor_one_use_per_day")
        ]

    def __str__(self) -> str:
        return f"{self.user_id}@{self.day}: {self.count}"


class Spend(models.Model):
    """What the tutor cost on one day, per model (decision ⑧).

    Summed per month for the budget page. Kept apart from the messages for
    the same reason as `DailyUse`: a student deleting a conversation must not
    erase what it cost. Holds no content.
    """

    day = models.DateField()
    model = models.CharField(max_length=64)
    replies = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=12, decimal_places=6, default=0)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["day", "model"], name="tutor_one_spend_per_day_model")
        ]

    def __str__(self) -> str:
        return f"{self.day} {self.model}: {self.cost_usd}"


class Budget(UpdatedModel):
    """The monthly limit staff set on the admin page (decision ⑧). One row."""

    #: In US dollars at API prices; 0 — not set.
    month_limit_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"{self.month_limit_usd} USD / month"


class Report(CreatedModel):
    """A student flags a tutor reply; staff see only these (decision ⑦).

    The question and the reply are copied in when the report is made: the
    student may still delete the conversation, and the report must keep what
    it is about. By reporting, the student shows these two texts to staff.
    """

    class Reason(models.TextChoices):
        WRONG = "wrong", "Noto'g'ri"
        SOLUTION = "solution", "Yechim berdi"
        HARMFUL = "harmful", "Zararli"
        OTHER = "other", "Boshqa"

    class Status(models.TextChoices):
        OPEN = "open", "Ochiq"
        ACCEPTED = "accepted", "Qabul qilindi"
        REJECTED = "rejected", "Rad etildi"

    reply = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="+")
    reason = models.CharField(max_length=10, choices=Reason.choices)
    note = models.CharField(max_length=500, blank=True)
    question_text = models.TextField(blank=True)
    reply_text = models.TextField()
    model = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["reply"],
                condition=models.Q(reply__isnull=False),
                name="tutor_one_report_per_reply",
            )
        ]
        indexes: ClassVar = [
            models.Index(fields=["status", "created_at"], name="tutor_report_queue")
        ]

    def __str__(self) -> str:
        return f"{self.reason}:{self.pk}"
