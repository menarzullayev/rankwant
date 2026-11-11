"""Community: discussion comments, votes and reports (decision 2026-11-11).

A comment belongs to a *target* named by type and id rather than by a
foreign key: the same thread engine serves problem discussions and blog
entries, and the problem lives in another app (`check_architecture`).
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.db.models import Q

from core.bases import CreatedModel, TimeStampedModel


class Target(models.TextChoices):
    PROBLEM = "problem", "Masala"
    ENTRY = "entry", "Blog posti"


class Comment(TimeStampedModel):
    """One comment in a thread. Replies form a tree (owner decision ①).

    `root` is the thread's first comment (null on the root itself), so a
    page of threads loads every reply in one query. Deleting by the
    author or hiding by moderation keeps the row: the replies under it
    stay attached and the thread does not break.
    """

    target_type = models.CharField(max_length=8, choices=Target.choices)
    target_id = models.PositiveIntegerField()
    author = models.ForeignKey(
        "core.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="community_comments",
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    root = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="thread"
    )
    depth = models.PositiveSmallIntegerField(default=0)
    body = models.TextField()
    #: The sum of votes, kept on the row so a page sorts and draws without
    #: counting (`Vote` stays the source of truth).
    score = models.IntegerField(default=0)
    report_count = models.PositiveSmallIntegerField(default=0)
    #: The author removed it: the text goes, the place in the thread stays.
    is_deleted = models.BooleanField(default=False)
    #: Moderation hid it (by reports or by staff); staff can bring it back.
    is_hidden = models.BooleanField(default=False, db_index=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["created_at", "pk"]
        indexes: ClassVar = [
            models.Index(
                fields=["target_type", "target_id", "root", "-created_at"], name="comment_thread"
            ),
            models.Index(fields=["author", "created_at"], name="comment_author"),
        ]

    def __str__(self) -> str:
        return f"{self.target_type}:{self.target_id} #{self.pk}"


class Kind(models.TextChoices):
    """What a vote or a report is about."""

    COMMENT = "comment", "Izoh"
    ENTRY = "entry", "Blog posti"


class Vote(CreatedModel):
    """One person's ±1 on a comment or an entry (owner decision ⑤: everyone).

    `author` is the author of what was voted on, copied at vote time: karma
    is the sum over this column (owner decision ③: all time).
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="community_votes")
    kind = models.CharField(max_length=8, choices=Kind.choices)
    object_id = models.PositiveIntegerField()
    value = models.SmallIntegerField()
    author = models.ForeignKey(
        "core.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="community_votes_received",
    )

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "kind", "object_id"], name="uniq_vote"),
            models.CheckConstraint(condition=Q(value__in=(-1, 1)), name="vote_is_one"),
        ]
        indexes: ClassVar = [models.Index(fields=["author", "created_at"], name="vote_author")]

    def __str__(self) -> str:
        return f"{self.user_id} {self.value:+d} {self.kind}:{self.object_id}"


class Report(CreatedModel):
    """A complaint about a comment or an entry (owner decision ⑥).

    Three different people reporting the same thing hide it at once; staff
    then accept (it stays hidden) or reject (it comes back).
    """

    class Reason(models.TextChoices):
        SPAM = "spam", "Spam yoki reklama"
        RUDE = "rude", "Haqorat"
        SPOILER = "spoiler", "Yechimni ochib beradi"
        OTHER = "other", "Boshqa"

    class Status(models.TextChoices):
        OPEN = "open", "Ochiq"
        ACCEPTED = "accepted", "Qabul qilindi"
        REJECTED = "rejected", "Rad etildi"

    reporter = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="community_reports"
    )
    kind = models.CharField(max_length=8, choices=Kind.choices)
    object_id = models.PositiveIntegerField()
    reason = models.CharField(max_length=8, choices=Reason.choices)
    note = models.CharField(max_length=300, blank=True)
    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.OPEN, db_index=True
    )
    handled_by = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    handled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["reporter", "kind", "object_id"], name="uniq_community_report"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.kind}:{self.object_id} — {self.reason}"
