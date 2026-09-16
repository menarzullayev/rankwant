"""Arena — jonli, taymerli savol-javob raundi.

Hamma bir vaqtda kiradi, savollar ketma-ket ochiladi, standings jonli.
Joriy savol SERVER VAQTIDAN hisoblanadi: `(now − start_at) ÷ soniya`.
Shu sababli har foydalanuvchi uchun alohida taymer saqlanmaydi va
mijoz vaqtni «orqaga surib» qo'shimcha vaqt ololmaydi.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from functools import cached_property
from typing import ClassVar

from django.db import models
from django.utils import timezone

from core.mixins import TimeWindowMixin


class ArenaRound(TimeWindowMixin, models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField(db_index=True)
    seconds_per_question = models.PositiveIntegerField(default=60)
    questions = models.ManyToManyField(
        "quizzes.Question", through="ArenaQuestion", related_name="arena_rounds"
    )
    #: Har ishtirokchiga raund tugagach (kunlik shiftga bo'ysunadi)
    reward_qvant = models.PositiveIntegerField(default=15)
    is_public = models.BooleanField(default=True)
    rewards_applied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-start_at"]

    def __str__(self) -> str:
        return self.slug

    @cached_property
    def _item_count(self) -> int:
        return self.items.count()

    @property
    def end_at(self) -> datetime:
        """Raund tugash vaqti — savollar soniga bog'liq.

        Sanoq ro'yxat so'rovidagi `question_count` annotatsiyasidan
        olinadi. Ilgari har murojaat alohida `COUNT` qilardi, `is_running`
        va `is_finished` esa ikkalasi ham shu yerga tayanadi — o'lchandi:
        bitta raundni serializatsiya qilish uchun uchta bir xil so'rov,
        ya'ni N raundda 3N.
        """
        count = self.question_count if hasattr(self, "question_count") else self._item_count
        return self.start_at + timedelta(seconds=self.seconds_per_question * count)

    @property
    def current_index(self) -> int | None:
        """Hozir ochiq savolning tartib raqami (0 dan), raund yurmasa None."""
        if not self.is_running:
            return None
        elapsed = (timezone.now() - self.start_at).total_seconds()
        return int(elapsed // self.seconds_per_question)

    def question_deadline(self, index: int) -> datetime:
        return self.start_at + timedelta(seconds=self.seconds_per_question * (index + 1))


class ArenaQuestion(models.Model):
    round = models.ForeignKey(ArenaRound, on_delete=models.CASCADE, related_name="items")
    question = models.ForeignKey(
        "quizzes.Question", on_delete=models.CASCADE, related_name="arena_items"
    )
    order = models.PositiveIntegerField()

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["round", "order"], name="uniq_arena_question_order"),
            models.UniqueConstraint(fields=["round", "question"], name="uniq_arena_question"),
        ]

    def __str__(self) -> str:
        return f"{self.round_id}#{self.order}"


class ArenaParticipation(models.Model):
    round = models.ForeignKey(ArenaRound, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="arena_runs")
    #: Tezlikka qarab ball: to'g'ri va tez — ko'proq
    score = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    #: Teng ballda kim tezroq — tiebreak
    total_ms = models.PositiveBigIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-score", "total_ms", "joined_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["round", "user"], name="uniq_arena_participant")
        ]

    def __str__(self) -> str:
        return f"{self.round_id} {self.user_id} {self.score}"


class ArenaAnswer(models.Model):
    participation = models.ForeignKey(
        ArenaParticipation, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey("quizzes.Question", on_delete=models.CASCADE, related_name="+")
    choice = models.ForeignKey("quizzes.Choice", on_delete=models.CASCADE, related_name="+")
    is_correct = models.BooleanField()
    elapsed_ms = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["participation", "question"], name="uniq_arena_answer_once"
            )
        ]

    def __str__(self) -> str:
        return f"{self.participation_id} q{self.question_id} {'+' if self.is_correct else '-'}"
