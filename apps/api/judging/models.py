"""Submit va verdict — 05-domain-model 🔒."""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.bases import CreatedModel
from judging.verdicts import Verdict

MAX_SOURCE_BYTES = 64 * 1024  # 08-technical-spec 🔒


class Attempt(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="attempts")
    problem = models.ForeignKey(
        "problems.Problem", on_delete=models.CASCADE, related_name="attempts"
    )
    #: Natija QAYSI revision asosida olingani (ADR 0052).
    #:
    #: ⚠️ Bu maydon `null` bo'lishi mumkin va shunday qoladi: 2026-09-30
    #: gacha olingan urinishlar qaysi paketda yurgizilganini bilib
    #: bo'lmaydi — ularni «birinchi revision» deb yozish tarixni
    #: o'ylab topish bo'lardi. Yangi urinishlarda to'ldiriladi.
    problem_revision = models.ForeignKey(
        "problems.ProblemRevision",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="attempts",
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
    #: Judge hozir qaysi testni bajarayotgani (1-based). Faqat RUNNING
    #: davomida to'ldiriladi; yakuniy verdiktda tozalanadi.
    running_test_index = models.PositiveIntegerField(null=True, blank=True)
    compile_output = models.TextField(blank=True)
    #: Judge telemetriyasi: worker, sandbox, queue_wait_ms, total_ms.
    #: `latency_ms` umumiy kechikishni beradi, bu esa sababini —
    #: navbatda kutishmi yoki bajarishmi (ADR-0004 sig'im rejasi).
    judge_meta = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    judged_at = models.DateTimeField(null=True, blank=True)
    #: Qotib qolgani uchun navbatga QAYTA qo'yilgan vaqt. Judge qayta
    #: ishga tushsa (deploy, OOM) navbatdan olingan ish yo'qoladi va
    #: urinish abadiy PENDING bo'lib qolardi. Bir marta qayta uriniladi;
    #: bu maydon ikkinchi marta urinmaslik uchun.
    requeued_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["user", "problem", "verdict"], name="attempt_solved_lookup"),
            models.Index(fields=["contest", "created_at"], name="attempt_contest_feed"),
            models.Index(fields=["problem", "-created_at"], name="attempt_problem_feed"),
            models.Index(fields=["verdict", "created_at"], name="attempt_pending_feed"),
            models.Index(fields=["user", "-created_at"], name="attempt_user_feed"),
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


class AttemptAnswer(models.Model):
    """One answer file of an `answer` task attempt (ADR-0053).

    The text lives in object storage; the row says which test it answers.
    A carried row points at the file of an earlier attempt: the solver did
    not send this test again, so their last answer for it still stands.
    """

    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    order = models.PositiveIntegerField()
    ref = models.CharField(max_length=255)
    size = models.PositiveIntegerField(default=0)
    carried = models.BooleanField(default=False)

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["attempt", "order"], name="uniq_attempt_answer")
        ]

    def __str__(self) -> str:
        return f"attempt {self.attempt_id} answer #{self.order}"


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


class CustomRun(CreatedModel):
    """PRD P0-4 — foydalanuvchi o'z stdin'i bilan kodni sinab ko'radi.

    Attempt EMAS: urinishlar tarixiga tushmaydi, reytingga ta'sir qilmaydi,
    masalaga bog'lanmaydi. Faqat "kodim ishlaydimi" savoliga javob.
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="custom_runs")
    language = models.ForeignKey(
        "problems.Language", on_delete=models.PROTECT, related_name="custom_runs"
    )
    source_code = models.TextField()
    stdin = models.TextField(blank=True)

    verdict = models.CharField(max_length=24, choices=Verdict.choices, default=Verdict.PENDING)
    stdout = models.TextField(blank=True)
    compile_output = models.TextField(blank=True)
    time_ms = models.PositiveIntegerField(default=0)
    memory_kb = models.PositiveIntegerField(default=0)

    judged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return f"custom #{self.pk} {self.verdict}"
