"""Submit va verdict — 05-domain-model 🔒."""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from judging.verdicts import Verdict

MAX_SOURCE_BYTES = 64 * 1024  # 08-technical-spec 🔒


class Attempt(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="attempts")
    problem = models.ForeignKey(
        "problems.Problem", on_delete=models.CASCADE, related_name="attempts"
    )
    contest = models.ForeignKey(
        "contests.Contest",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attempts",
    )
    language = models.ForeignKey(
        "problems.Language", on_delete=models.PROTECT, related_name="attempts"
    )

    source_code = models.TextField()
    source_size = models.PositiveIntegerField(default=0)

    verdict = models.CharField(
        max_length=24, choices=Verdict.choices, default=Verdict.PENDING, db_index=True
    )
    score = models.PositiveIntegerField(default=0)
    time_ms = models.PositiveIntegerField(default=0)
    memory_kb = models.PositiveIntegerField(default=0)
    failed_test_index = models.PositiveIntegerField(null=True, blank=True)
    compile_output = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    judged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["user", "problem", "verdict"], name="attempt_solved_lookup"),
            models.Index(fields=["contest", "created_at"], name="attempt_contest_feed"),
            models.Index(fields=["problem", "-created_at"], name="attempt_problem_feed"),
        ]

    def __str__(self) -> str:
        return f"#{self.pk} {self.user_id} {self.problem_id} {self.verdict}"

    def save(self, *args: object, **kwargs: object) -> None:
        self.source_size = len(self.source_code.encode())
        super().save(*args, **kwargs)  # type: ignore[arg-type]

    @property
    def latency_ms(self) -> int | None:
        """Submit dan verdict gacha — NFR p50<5s, p95<15s o'lchovi."""
        if self.judged_at is None:
            return None
        return int((self.judged_at - self.created_at).total_seconds() * 1000)


class AttemptTestResult(models.Model):
    """Per-test natija. Contest davomida boshqa foydalanuvchiga ko'rsatilmaydi."""

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="test_results")
    index = models.PositiveIntegerField()
    verdict = models.CharField(max_length=24, choices=Verdict.choices)
    time_ms = models.PositiveIntegerField(default=0)
    memory_kb = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["index"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["attempt", "index"], name="uniq_attempt_test")
        ]

    def __str__(self) -> str:
        return f"attempt {self.attempt_id} test #{self.index}: {self.verdict}"
