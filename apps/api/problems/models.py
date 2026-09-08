"""Masala banki — 05-domain-model 🔒."""

from __future__ import annotations

from typing import Any, ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models, transaction

DIFFICULTY_MIN = 800
DIFFICULTY_MAX = 3500
DIFFICULTY_STEP = 100

# 04-prd § Poydevor — qiyinlik shkalasi. Foydalanuvchi raqamni emas,
# DARAJANI ko'radi.
#
# Pastki yarmi ataylab mayda: 800–1800 oralig'ida o'quvchi oylab turadi
# va keng daraja ichida siljish sezilmasdi (KEP shu sababli 7 ta daraja
# ishlatadi). Yuqori qismida masala kam, mayda bo'lish keraksiz.
DIFFICULTY_LEVELS: tuple[tuple[int, str, str], ...] = (
    (1000, "beginner", "Boshlang'ich"),
    (1200, "basic", "Asosiy"),
    (1500, "intermediate", "O'rta"),
    (1800, "upper", "Yaxshi"),
    (2200, "hard", "Qiyin"),
    (2700, "expert", "Ekspert"),
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

    code = models.SlugField(unique=True)  # cpp23, py313, java21
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=50, blank=True)
    compile_cmd = models.JSONField(default=list, blank=True)  # bo'sh = kompilyatsiya yo'q
    run_cmd = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} {self.version}".strip()


class ProblemCodeSequence(models.Model):
    """Berilgan oxirgi ommaviy raqam.

    `max(code) + 1` yetarli emas: eng oxirgi masala o'chirilsa uning
    raqami bo'shab qolar va keyingi masalaga o'tardi — tarqalgan `#0431`
    havolasi boshqa masalani ko'rsatib qolardi. Hisoblagich faqat oldinga
    yuradi.
    """

    value = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"#{self.value:04d}"

    @classmethod
    def next_code(cls) -> int:
        counter = cls.objects.select_for_update().first()
        if counter is None:
            counter = cls.objects.create(value=0)
            counter = cls.objects.select_for_update().get(pk=counter.pk)
        counter.value += 1
        counter.save(update_fields=["value"])
        return counter.value


class Problem(models.Model):
    class Checker(models.TextChoices):
        STANDARD = "standard", "Standart"
        SPECIAL = "special", "Maxsus"
        INTERACTIVE = "interactive", "Interactive"

    slug = models.SlugField(unique=True, max_length=100)
    #: Ommaviy qisqa raqam — `#0431`. Slug'dan farqli: og'zaki muomala
    #: uchun ("431-masalani yeching") va hech qachon o'zgarmaydi.
    #: `pk` EMAS: qoralamalar va o'chirilgan yozuvlar teshik qoldirardi,
    #: shu bois raqam faqat masala e'lon qilinganda beriladi.
    code = models.PositiveIntegerField(unique=True, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=200)
    statement = models.TextField(help_text="Markdown + LaTeX")
    # Kiruvchi/chiquvchi alohida maydon, statement ichidagi sarlavha emas:
    # RoboContest, KEP va Codeforces uchalasida ham bu qat'iy bo'lim va
    # solver ularni matndan ajratib qidiradi. Konvensiyaga tayanish
    # muallifga bog'liq bo'lardi, maydon esa tuzilmani kafolatlaydi.
    input_format = models.TextField(blank=True, help_text="Markdown + LaTeX")
    output_format = models.TextField(blank=True, help_text="Markdown + LaTeX")
    #: Codeforces «Note» — namunalar nega shunday ekanini tushuntiradi.
    note = models.TextField(blank=True, help_text="Markdown + LaTeX")
    #: Yechim tahlili. Yechmagan foydalanuvchiga spoyler sifatida yopiq.
    editorial = models.TextField(blank=True, help_text="Markdown + LaTeX")
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

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Raqam e'lon qilinganda beriladi — barcha yo'llarda (admin, staff
        # API, seed) bir xil ishlashi uchun `save()` da. Yagona indeks
        # poyga holatini ushlaydi; publish kamdan-kam amal, shu bois
        # qayta urinish yetarli.
        for _ in range(4):
            if not self.is_public or self.code:
                return super().save(*args, **kwargs)
            try:
                with transaction.atomic():
                    self.code = ProblemCodeSequence.next_code()
                    return super().save(*args, **kwargs)
            except IntegrityError:
                self.code = None
                kwargs.pop("force_insert", None)
        raise IntegrityError("masala raqamini berib bo'lmadi")

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


class Favourite(models.Model):
    """Keyinroq qaytish uchun belgilangan masala.

    RoboContest va Codeforces'dagi «sevimlilar» — uzun arxivda yo'qolib
    ketmaslikning eng oddiy usuli.
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="favourites")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="favourites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="uniq_favourite")
        ]
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.problem.slug}"


class ProblemRating(models.Model):
    """Foydalanuvchining masalaga bergan bahosi (1–5).

    RoboContest sahifada «3.2 · 10 baholar» ko'rsatadi — muallif uchun
    ham, tanlayotgan solver uchun ham signal.
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="problem_ratings")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="uniq_problem_rating")
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug}: {self.score}"
