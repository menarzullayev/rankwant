"""Testlar (P2-6) va savol banki.

Savol BANKI test'dan alohida: bitta savol ham testda, ham Arena
raundida ishlatiladi. Aks holda har raund uchun savollar qayta
yozilardi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.bases import CreatedModel


class QuestionFolder(CreatedModel):
    """A teacher's folder in their own question bank (ADR-0061 § 5)."""

    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="question_folders"
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering: ClassVar = ["name"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["owner", "name"], name="uniq_question_folder")
        ]

    def __str__(self) -> str:
        return self.name


class Question(CreatedModel):
    class Kind(models.TextChoices):
        #: One correct choice — the staff bank and the arena use only this.
        SINGLE = "single", "Bitta to'g'ri"
        #: Several correct choices: credit only for exactly the right set.
        MULTIPLE = "multiple", "Bir nechta to'g'ri"
        #: A number, right within `tolerance`.
        NUMBER = "number", "Son"
        #: A short text; case and spaces do not matter.
        TEXT = "text", "Qisqa matn"

    #: `None` — the staff bank (public quizzes, the arena); a user — that
    #: teacher's own bank, seen by nobody else.
    owner = models.ForeignKey(
        "core.User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    folder = models.ForeignKey(
        QuestionFolder, null=True, blank=True, on_delete=models.SET_NULL, related_name="questions"
    )
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.SINGLE)
    text = models.TextField(help_text="Markdown + LaTeX")
    #: A code snippet shown under the text, highlighted (any kind).
    code = models.TextField(blank=True)
    code_language = models.CharField(max_length=20, blank=True)
    answer_number = models.FloatField(null=True, blank=True)
    tolerance = models.FloatField(default=0)
    #: Accepted answers for `text`, one per line.
    answer_text = models.TextField(blank=True)
    explanation = models.TextField(blank=True, help_text="Javobdan keyin ko'rsatiladi")
    topics = models.ManyToManyField("problems.Topic", blank=True, related_name="questions")
    #: Masala qiyinligi shkalasida (800–3500) — tavsiya va Arena saralash uchun
    difficulty = models.PositiveIntegerField(default=800)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return self.text[:60]

    @property
    def correct_choice_id(self) -> int | None:
        """To'g'ri variant — RO'YXATDAN, `filter()` bilan emas.

        `filter()` prefetch keshini chetlab o'tib yangi so'rov beradi.
        `grade()` esa aynan shu maqsadda `prefetch_related` qiladi:
        o'lchandi — 10 savolli test 12 ta so'rov bajarardi, ikkitasi
        yetarli bo'lgan joyda. Variantlar soni bir savolda kichik.
        """
        for choice in self.choices.all():
            if choice.is_correct:
                return choice.pk
        return None


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


class Quiz(CreatedModel):
    #: `None` — a public quiz in the catalogue; a user — a teacher's quiz,
    #: open only to the classes it is given to and worth no Qvant
    #: (ADR-0061 § 5, owner decision ⑪).
    owner = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.CASCADE, related_name="quizzes"
    )
    #: Minutes from `start`; `None` — no limit.
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
    one_attempt = models.BooleanField(default=False)
    #: Right answers are shown after this moment; `None` — as soon as the
    #: attempt is finished.
    answers_after = models.DateTimeField(null=True, blank=True)
    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(Question, through="QuizQuestion", related_name="quizzes")
    #: Birinchi yakunlashda beriladi; kunlik shiftga bo'ysunadi (ADR-0002)
    reward_qvant = models.PositiveIntegerField(default=10)
    is_published = models.BooleanField(default=False, db_index=True)

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


class QuizAttempt(CreatedModel):
    """Bitta topshirish. Qayta topshirish mumkin, lekin Qvant faqat birinchisida."""

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    #: {question_id: answer} — a choice id, a list of them, a number or a
    #: text, by the question's kind; an unanswered question is absent.
    answers = models.JSONField(default=dict)
    #: Set by `start` (a timed quiz); a submit without `start` has none.
    started_at = models.DateTimeField(null=True, blank=True)
    #: `None` — started and not submitted yet.
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    qvant_awarded = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [models.Index(fields=["user", "quiz"], name="quiz_attempt_lookup")]

    def __str__(self) -> str:
        return f"{self.user_id} {self.quiz_id} {self.score}/{self.total}"
