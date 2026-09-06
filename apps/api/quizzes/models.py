"""Testlar (P2-6) va savol banki.

Savol BANKI test'dan alohida: bitta savol ham testda, ham Arena
raundida ishlatiladi. Aks holda har raund uchun savollar qayta
yozilardi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models


class Question(models.Model):
    text = models.TextField(help_text="Markdown + LaTeX")
    explanation = models.TextField(blank=True, help_text="Javobdan keyin ko'rsatiladi")
    topics = models.ManyToManyField("problems.Topic", blank=True, related_name="questions")
    #: Masala qiyinligi shkalasida (800–3500) — tavsiya va Arena saralash uchun
    difficulty = models.PositiveIntegerField(default=800)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return self.text[:60]

    @property
    def correct_choice_id(self) -> int | None:
        choice = self.choices.filter(is_correct=True).first()
        return choice.pk if choice else None


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    order = models.PositiveIntegerField()
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["question", "order"], name="uniq_choice_order")
        ]

    def __str__(self) -> str:
        return self.text[:40]


class Quiz(models.Model):
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(Question, through="QuizQuestion", related_name="quizzes")
    #: Birinchi yakunlashda beriladi; kunlik shiftga bo'ysunadi (ADR-0002)
    reward_qvant = models.PositiveIntegerField(default=10)
    is_published = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        verbose_name_plural = "quizzes"

    def __str__(self) -> str:
        return self.slug


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="items")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="quiz_items")
    order = models.PositiveIntegerField()

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["quiz", "order"], name="uniq_quiz_question_order"),
            models.UniqueConstraint(fields=["quiz", "question"], name="uniq_quiz_question"),
        ]

    def __str__(self) -> str:
        return f"{self.quiz_id}#{self.order}"


class QuizAttempt(models.Model):
    """Bitta topshirish. Qayta topshirish mumkin, lekin Qvant faqat birinchisida."""

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    #: {question_id: choice_id} — tanlanmagan savol yo'q bo'ladi
    answers = models.JSONField(default=dict)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    qvant_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [models.Index(fields=["user", "quiz"], name="quiz_attempt_lookup")]

    def __str__(self) -> str:
        return f"{self.user_id} {self.quiz_id} {self.score}/{self.total}"
