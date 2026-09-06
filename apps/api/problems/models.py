"""Masala banki — 05-domain-model 🔒."""

from __future__ import annotations

from typing import ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

DIFFICULTY_MIN = 800
DIFFICULTY_MAX = 3500
DIFFICULTY_STEP = 100

# 04-prd § Poydevor — qiyinlik shkalasi. Foydalanuvchi raqamni emas,
# DARAJANI ko'radi.
DIFFICULTY_LEVELS: tuple[tuple[int, str, str], ...] = (
    (1200, "beginner", "Boshlang'ich"),
    (1600, "intermediate", "O'rta"),
    (2100, "hard", "Qiyin"),
    (2600, "expert", "Ekspert"),
    (10**9, "master", "Master"),
)


def difficulty_level(value: int) -> tuple[str, str]:
    """Qiyinlik raqamini (kod, nom) juftligiga aylantiradi."""
    for upper, code, label in DIFFICULTY_LEVELS:
        if value < upper:
            return code, label
    return DIFFICULTY_LEVELS[-1][1], DIFFICULTY_LEVELS[-1][2]


class Topic(models.Model):
    slug = models.SlugField(unique=True)
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100, blank=True)
    name_en = models.CharField(max_length=100, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )

    def __str__(self) -> str:
        return self.name_uz


class Language(models.Model):
    """Judge tillari — til obrazlari bilan bir manbadan (ADR-0004)."""

    code = models.SlugField(unique=True)  # cpp23, py312, java17
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=50, blank=True)
    compile_cmd = models.JSONField(default=list, blank=True)  # bo'sh = kompilyatsiya yo'q
    run_cmd = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} {self.version}".strip()


class Problem(models.Model):
    class Checker(models.TextChoices):
        STANDARD = "standard", "Standart"
        SPECIAL = "special", "Maxsus"
        INTERACTIVE = "interactive", "Interactive"

    slug = models.SlugField(unique=True, max_length=100)
    title = models.CharField(max_length=200)
    statement = models.TextField(help_text="Markdown + LaTeX")
    statement_locale = models.CharField(max_length=2, default="uz")

    difficulty = models.PositiveIntegerField(
        validators=[MinValueValidator(DIFFICULTY_MIN), MaxValueValidator(DIFFICULTY_MAX)],
        db_index=True,
        help_text=f"{DIFFICULTY_MIN}–{DIFFICULTY_MAX}, qadam {DIFFICULTY_STEP}",
    )
    topics = models.ManyToManyField(Topic, blank=True, related_name="problems")

    time_limit_ms = models.PositiveIntegerField(default=1000)
    memory_limit_kb = models.PositiveIntegerField(default=262144)
    checker_type = models.CharField(
        max_length=16, choices=Checker.choices, default=Checker.STANDARD
    )
    interactor_source = models.TextField(blank=True)
    interactor_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    is_public = models.BooleanField(default=False, db_index=True)
    author = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="problems"
    )
    source = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)

    # Denormalizatsiya — filtr va statistika uchun
    solved_count = models.PositiveIntegerField(default=0)
    attempt_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["difficulty", "slug"]

    def __str__(self) -> str:
        return f"{self.slug} ({self.difficulty})"

    @property
    def level(self) -> str:
        return difficulty_level(self.difficulty)[0]

    @property
    def level_label(self) -> str:
        return difficulty_level(self.difficulty)[1]

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.difficulty % DIFFICULTY_STEP:
            raise ValidationError(
                {"difficulty": f"Qiymat {DIFFICULTY_STEP} ga karrali bo'lishi kerak"}
            )


class Subtask(models.Model):
    """IOI scoring uchun."""

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="subtasks")
    order = models.PositiveIntegerField()
    points = models.PositiveIntegerField(default=0)
    scoring = models.CharField(
        max_length=8, choices=[("min", "min"), ("sum", "sum")], default="min"
    )

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem", "order"], name="uniq_subtask_order")
        ]

    def __str__(self) -> str:
        return f"{self.problem_id} subtask #{self.order}"


class TestCase(models.Model):
    """Test ma'lumotlari DB da EMAS — S3/R2 da (05-domain-model)."""

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="tests")
    order = models.PositiveIntegerField()
    input_ref = models.CharField(max_length=500)
    output_ref = models.CharField(max_length=500)
    is_sample = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)
    subtask = models.ForeignKey(
        Subtask, null=True, blank=True, on_delete=models.SET_NULL, related_name="tests"
    )

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem", "order"], name="uniq_test_order")
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug} #{self.order}"
