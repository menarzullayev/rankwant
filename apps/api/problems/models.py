"""Masala banki — 05-domain-model 🔒."""

from __future__ import annotations

from typing import Any, ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import IntegrityError, models, transaction

from core.bases import CreatedModel, TimeStampedModel, UpdatedModel

# Re-exported: the filters and two data migrations import it from here.
from core.search import normalize_search as normalize_search

#: Same rule the judge enforces (services/judge-go/judge.go `sourceFileName`):
#: a bare name with an extension, so it can never point outside the work dir.
SOURCE_FILE_PATTERN = r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+\Z"

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
    #: Nomning qidiruv shakli. Slug yetarli emas: birlashtirilgan
    #: mavzuda u inglizcha qolishi mumkin (`dp` = «Dinamik dasturlash»),
    #: ya'ni «dinamik» so'rovi slug orqali hech narsa topmasdi.
    name_search = models.CharField(max_length=100, blank=True, db_index=True)
    name_ru = models.CharField(max_length=100, blank=True)
    name_en = models.CharField(max_length=100, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )

    def __str__(self) -> str:
        return self.name_uz

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.name_search = normalize_search(self.name_uz)
        super().save(*args, **kwargs)


class Language(models.Model):
    """Judge tillari — til obrazlari bilan bir manbadan (ADR-0004)."""

    code = models.SlugField(unique=True)  # cpp23, py313, java21
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=50, blank=True)
    #: The name the judge saves the source under (main.cpp, Main.java, main.kt).
    #: Compilers pick the language from the extension and JVM languages want the
    #: class name in it. Blank keeps the judge's old code-prefix mapping.
    source_file = models.CharField(
        max_length=64,
        blank=True,
        default="",
        validators=[RegexValidator(SOURCE_FILE_PATTERN, "Faqat fayl nomi: main.cpp, Main.java")],
    )
    compile_cmd = models.JSONField(default=list, blank=True)  # bo'sh = kompilyatsiya yo'q
    run_cmd = models.JSONField(default=list)
    #: Sandboxdagi jarayon/OQIM chegarasi — cgroup `pids.max` ikkalasini
    #: ham sanaydi. C++ va Python uchun bitta yetadi, JVM esa bo'sh
    #: dasturda ham 18 ta oqim ochadi (o'lchandi) va 1 bilan umuman
    #: ishga tushmasdi.
    process_limit = models.PositiveSmallIntegerField(default=1)
    #: CPU budget for compiling one submission. kotlinc needs ~5 s for A+B alone
    #: (measured in the judge image), so one number cannot fit all.
    compile_time_ms = models.PositiveIntegerField(default=10_000)
    #: The sandbox mounts a procfs showing only its own processes instead of
    #: masking /proc. CoreCLR, Dart, Julia and the Swift compiler do not start
    #: without /proc/self (ADR-0022).
    proc_self = models.BooleanField(default=False)
    #: RLIMIT_NOFILE for this language's programs; 0 keeps the judge's 64.
    #: R and PowerShell refuse to start below ~192 (measured).
    open_files = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} {self.version}".strip()

    def judge_spec(self) -> dict[str, Any]:
        """The `language` object of a judge job (services/bakeoff/protocol.md).

        Every job builder goes through here, so a field added to the contract
        cannot be forgotten in one of them.
        """
        return {
            "code": self.code,
            "source_file": self.source_file,
            "compile": self.compile_cmd,
            "run": self.run_cmd,
            "proc_self": self.proc_self,
            "open_files": self.open_files,
        }


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
        # Never below a code that already exists. A code can be set without
        # this counter (an import, the admin, a fixture); the counter then
        # hands out a number that is taken, and the caller's retry cannot
        # help — its savepoint rolls this increment back, so every attempt
        # gets the same number (measured: four identical UNIQUE failures,
        # then "masala raqamini berib bo'lmadi").
        taken = Problem.objects.aggregate(top=models.Max("code"))["top"] or 0
        counter.value = max(counter.value, taken) + 1
        counter.save(update_fields=["value"])
        return counter.value


class Problem(TimeStampedModel):
    class Checker(models.TextChoices):
        STANDARD = "standard", "Standart"
        SPECIAL = "special", "Maxsus"
        INTERACTIVE = "interactive", "Interactive"
        #: Checker to'g'ri/noto'g'ri emas, 0–100 oralig'ida SIFAT bahosini
        #: qaytaradi (TSP yo'l uzunligi, qadoqlar soni). Ball mutlaq —
        #: boshqalarning yechimiga bog'liq emas, ya'ni qayta hisoblash yo'q.
        SCORER = "scorer", "Skoring"

    slug = models.SlugField(unique=True, max_length=100)
    #: Ommaviy qisqa raqam — `#0431`. Slug'dan farqli: og'zaki muomala
    #: uchun ("431-masalani yeching") va hech qachon o'zgarmaydi.
    #: `pk` EMAS: qoralamalar va o'chirilgan yozuvlar teshik qoldirardi,
    #: shu bois raqam faqat masala e'lon qilinganda beriladi.
    code = models.PositiveIntegerField(unique=True, null=True, blank=True, db_index=True)
    title = models.CharField(max_length=200)
    #: Sarlavhaning qidiruv shakli — apostrofsiz, kichik harfda.
    #: `save()` da to'ldiriladi, qo'lda yozilmaydi.
    title_search = models.CharField(max_length=200, blank=True, db_index=True)
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
    #: Mualliflar (ADR-0025): o'z draft masalasini yaratadi, bayonot va
    #: editorialni tahrirlaydi, o'z draftining testlarini yuklaydi; nashr
    #: (`is_public=True`) — staff-ops. Bir muallifda ko'p masala bo'lishi
    #: mumkin, bir masalada ko'p muallif — shuning uchun M2M.
    authors = models.ManyToManyField(
        "core.User",
        blank=True,
        related_name="authored_problems",
        help_text="O'z draft masalasini boshqaradi; nashr — staff-ops (ADR-0025)",
    )

    time_limit_ms = models.PositiveIntegerField(default=1000)
    memory_limit_kb = models.PositiveIntegerField(default=262144)
    checker_type = models.CharField(
        max_length=16, choices=Checker.choices, default=Checker.STANDARD
    )

    class Readiness(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        NEEDS_TESTS = "needs_tests", "Test kerak"
        HAS_HIDDEN_TESTS = "has_hidden_tests", "Yashirin test bor"
        CHECKER_VALIDATED = "checker_validated", "Checker tekshirilgan"
        REF_SOLUTION_VERIFIED = "ref_solution_verified", "Etalon tekshirilgan"
        VALIDATED = "validated", "Tasdiqlangan"
        LEGACY_UNVERIFIED = "legacy_unverified", "Arxiv (tekshirilmagan)"
        BLOCKED = "blocked", "Bloklangan"
        NEEDS_REVIEW = "needs_review", "Ko'rik kerak"

    readiness = models.CharField(
        max_length=24,
        choices=Readiness.choices,
        default=Readiness.DRAFT,
        db_index=True,
    )
    #: Hozir nashr qilingan revision (ADR 0052). `null` — hech qachon nashr
    #: qilinmagan. Ommaviy API shu revisionni ko'rsatadi, ishchi nusxani
    #: emas: ya'ni tahrir davom etsa ham o'quvchi barqaror paketni ko'radi.
    current_revision = models.ForeignKey(
        "ProblemRevision",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    #: Checker qachon tekshirilgani (PROMPT_0 §2/§9). Buzuq checker eng
    #: yomon holat: u to'g'ri yechimni rad qiladi yoki xatoni o'tkazib
    #: yuboradi va natija «nima bo'lganda ham» noto'g'ri bo'ladi.
    #: `null` — tekshirilmagan.
    checker_verified_at = models.DateTimeField(null=True, blank=True)

    class IoMode(models.TextChoices):
        STDIO = "stdio", "Stdin/stdout"
        #: Robocontest uslubi: `input.txt` dan o'qiydi, `output.txt` ga yozadi;
        #: stdin/stdout yechimlari ham o'tadi (judge ikkala javobni tekshiradi).
        BOTH = "both", "Stdin/stdout yoki fayl"

    io_mode = models.CharField(
        max_length=8,
        choices=IoMode.choices,
        default=IoMode.STDIO,
        help_text="both: input.txt/output.txt ham, stdin/stdout ham qabul qilinadi.",
    )

    class TaskKind(models.TextChoices):
        """What a solver submits and how it is run (ADR-0053). The third
        axis: `io_mode` says where the answer travels, `checker_type` who
        grades it."""

        PROGRAM = "program", "Whole program"
        #: The solver writes a function; the author's harness is the program.
        FUNCTION = "function", "Function"
        #: The solver sends the answers themselves; no program is run.
        ANSWER = "answer", "Answer files"

    task_kind = models.CharField(
        max_length=16,
        choices=TaskKind.choices,
        default=TaskKind.PROGRAM,
        help_text="function: the submission is inserted into the per-language harness.",
    )
    interactor_source = models.TextField(blank=True)
    interactor_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    #: `special` va `scorer` uchun checker dasturi — testlib chaqiruvi:
    #: `checker <input> <output> <answer>`. Interactor kabi ISHONCHLI:
    #: masala bilan birga keladi va sandbox tashqarisida ishlaydi.
    #:
    #: Judge buni allaqachon biladi, model tomonida esa yo'q edi: `special`
    #: tanlangan masalaga har yuborish «checker dasturi berilmagan» degan
    #: IE qaytarardi.
    checker_source = models.TextField(blank=True)
    checker_language = models.ForeignKey(
        Language, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    is_public = models.BooleanField(default=False, db_index=True)
    author = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="problems"
    )
    source = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)

    # Denormalizatsiya — filtr va statistika uchun
    #: Import qilingan arxivning xom reytingi (KEP 100–2400). Bizning
    #: shkalaga chiziqli o'tkaziladi, lekin manba yo'qolmasin — keyin
    #: qayta xaritalash kerak bo'lishi mumkin.
    source_rating = models.PositiveIntegerField(null=True, blank=True)
    image = models.URLField(blank=True)
    #: Qisman ball beriladimi. Qanday hisoblanishi `subtasks` va
    #: `checker_type` bilan aniqlanadi: subtask bo'lsa IOI, `scorer`
    #: bo'lsa checker qaytargan son.
    partial_scoring = models.BooleanField(default=False)
    #: Import qilingan tarix. O'z bahoimiz 1–5 yulduz (`ProblemRating`),
    #: bular esa manbadagi ovozlar — aralashtirilmaydi.
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    #: Tahlilni yechmasdan ochish narxi, Qvant (ADR-0013). 0 — bepul.
    editorial_price = models.PositiveIntegerField(default=30)

    solved_count = models.PositiveIntegerField(default=0)
    attempt_count = models.PositiveIntegerField(default=0)
    #: Masala sahifasi ochilishi. «Ko'p ko'rilgan» ro'yxati uchun; yechish
    #: statistikasidan farqli — ko'rgan, lekin urinmaganlarni ham sanaydi.
    view_count = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering: ClassVar = ["difficulty", "slug"]
        indexes: ClassVar = [
            models.Index(fields=["is_public", "difficulty"], name="problem_public_diff"),
            models.Index(fields=["readiness", "is_public"], name="problem_readiness_pub"),
        ]

    def __str__(self) -> str:
        return f"{self.slug} ({self.difficulty})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # `User.solved_count` counts public problems only (ADR-0024), so a
        # change of visibility moves this problem's solvers up or down by one.
        update_fields = kwargs.get("update_fields")
        was_public = None
        if self.pk is not None and (update_fields is None or "is_public" in update_fields):
            was_public = (
                type(self).objects.filter(pk=self.pk).values_list("is_public", flat=True).first()
            )
        self._save_with_code(*args, **kwargs)
        if was_public is not None and was_public != self.is_public:
            from ratings.services import on_problem_visibility_changed

            on_problem_visibility_changed(self.pk, self.is_public)

    def _save_with_code(self, *args: Any, **kwargs: Any) -> None:
        self.title_search = normalize_search(self.title)
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

        from problems.readiness import assert_transition, gate, requirement_error

        if self.difficulty % DIFFICULTY_STEP:
            raise ValidationError({"difficulty": f"Value must be a multiple of {DIFFICULTY_STEP}"})

        # The Django admin can set `io_mode`; the staff API cannot. Both
        # must refuse a pair of modes the judge does not implement.
        from problems.evaluation import combination_error, task_kind_error

        invalid = combination_error(self.io_mode, self.checker_type) or task_kind_error(
            self.task_kind, self.io_mode, self.checker_type
        )
        if invalid:
            raise ValidationError({"checker_type": invalid})

        # ADR 0049 — R10: readiness moves one step at a time, and every step
        # has a condition (S1/S2/S3). The previous value comes from the
        # DATABASE: `full_clean()` sees the in-memory target, not where the
        # row currently sits.
        #
        # Order matters. The transition is checked FIRST, so a jump such as
        # `draft -> validated` is reported as "is not allowed" rather than as
        # whichever condition happens to be unmet.
        previous = self._stored_readiness()
        if previous is not None:
            assert_transition(previous, self.readiness)

        error = requirement_error(self, self.readiness)
        if error:
            gate(error)

    def _stored_readiness(self) -> str | None:
        """The readiness this row currently has in the database, or `None`."""
        if self.pk is None:
            return None
        return Problem.objects.filter(pk=self.pk).values_list("readiness", flat=True).first()


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

    class Origin(models.TextChoices):
        AUTHOR = "author", "Muallif"
        #: Muvaffaqiyatli hack testi (ADR-0020). Manbani bilish kerak:
        #: hack testi keyin qo'shilgan, ya'ni eski `AC` lar uni ko'rmagan
        #: va nega qayta tekshirilgani shu ustundan ko'rinadi.
        HACK = "hack", "Hack"

    class Group(models.TextChoices):
        """Testning SEMANTIK toifasi — `origin` dan butunlay boshqa o'q.

        `origin` — test QAYERDAN kelgan (muallif yoki hack).
        `group`  — test NIMANI tekshiradi (namuna, chegara, tasodifiy...).

        Ikkisi bir-birini almashtirmaydi: muallif yozgan chegara testi
        `origin=author, group=boundary`; hack'dan kelgan test esa
        `origin=hack, group=adversarial`.

        Siyosat (ko'rinish, nashr talabi) — `problems/testgroups.py` da.
        Modelda faqat tasnif turadi, qarorlar bitta joyda.
        """

        SAMPLE = "sample", "Namuna"
        MINIMAL = "minimal", "Minimal"
        BOUNDARY = "boundary", "Chegara"
        SPECIAL = "special", "Alohida holat"
        RANDOM = "random", "Tasodifiy"
        ADVERSARIAL = "adversarial", "Qarshi"
        MAXIMUM = "maximum", "Maksimal"
        STRESS = "stress", "Stress"
        #: Faqat KO'CHIRISH holati: 2026-09-30 gacha yozilgan testlarda tasnif
        #: yo'q edi. Nashr darvozasi buni «tasniflanmagan» deb qaraydi, ya'ni
        #: yangi kontent bu qiymatni ishlatmasligi kerak.
        UNCLASSIFIED = "unclassified", "Tasniflanmagan"

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="tests")
    order = models.PositiveIntegerField()
    input_ref = models.CharField(max_length=500)
    output_ref = models.CharField(max_length=500)
    is_sample = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)
    subtask = models.ForeignKey(
        Subtask, null=True, blank=True, on_delete=models.SET_NULL, related_name="tests"
    )
    origin = models.CharField(max_length=8, choices=Origin.choices, default=Origin.AUTHOR)
    group = models.CharField(
        max_length=16,
        choices=Group.choices,
        default=Group.UNCLASSIFIED,
        help_text="Semantik toifa; nashr talabi `problems/testgroups.py` da.",
    )

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem", "order"], name="uniq_test_order")
        ]
        indexes: ClassVar = [
            # Nashr darvozasi va judge siyosati guruh bo'yicha so'raydi.
            models.Index(fields=["problem", "group"], name="test_problem_group_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug} #{self.order}"


class ProblemLanguage(models.Model):
    """Masalaga xos til sozlamalari.

    Ikki vazifasi bor. Birinchisi — RUXSAT: masalada satr bo'lsa, faqat
    sanab o'tilgan tillar qabul qilinadi (interaktiv masalada ba'zi til
    qo'llab-quvvatlanmaydi). Satr umuman bo'lmasa hamma faol til ochiq.

    Ikkinchisi — USTMA-UST limit: Python C++ dan sekinroq, shu bois
    unga ko'proq vaqt beriladi. Bo'sh qoldirilsa masala limiti ishlaydi.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="languages")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="problems")
    time_limit_ms = models.PositiveIntegerField(null=True, blank=True)
    memory_limit_kb = models.PositiveIntegerField(null=True, blank=True)
    code_template = models.TextField(blank=True)
    #: `task_kind = function` only: the program around the submission, with
    #: `{{SOLUTION}}` alone on one line (`problems/taskkinds.py`). Shown to
    #: solvers, so it must not hold an expected answer.
    harness = models.TextField(blank=True)

    class Meta:
        ordering: ClassVar = ["language__name"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem", "language"], name="uniq_problem_language")
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug} · {self.language.code}"


class SimilarProblem(models.Model):
    """O'xshashlik grafi. Yo'nalishli: A→B bor bo'lsa B→A shart emas."""

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="similar_to")
    similar = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="similar_from")
    score = models.FloatField()
    #: Kim hisoblagan — import qilingan grafni o'zimizniki bilan
    #: aralashtirib yubormaslik uchun.
    source = models.CharField(max_length=32, default="import")

    class Meta:
        ordering: ClassVar = ["-score"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem", "similar"], name="uniq_similar_problem")
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug} ~ {self.similar.slug} ({self.score:.2f})"


class ProblemAttachment(models.Model):
    """Masalaga biriktirilgan fayl — rasm, ma'lumot fayli, shablon."""

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="attachments")
    name = models.CharField(max_length=200)
    url = models.URLField()
    size_bytes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["name"]

    def __str__(self) -> str:
        return f"{self.problem.slug} · {self.name}"


class Validator(UpdatedModel):
    """Kirish validatori — test cheklovlarga mosligini tekshiruvchi dastur.

    Muallif uchun emas, HACKING uchun: ishtirokchi boshqaning yechimini
    sindirish uchun test yuborganda, u test avval shu validatordan
    o'tishi kerak. Aks holda buzuq kiritma bilan istalgan yechimni
    «sindirish» mumkin bo'lardi. Shu sababli u sandbox'da, ishonchsiz
    kiritma ustida ishlaydi.
    """

    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name="validator")
    language = models.ForeignKey(Language, on_delete=models.PROTECT, related_name="validators")
    source = models.TextField()
    #: Validator ishonchli dastur, lekin KIRITMASI ishonchsiz — u cheksiz
    #: aylanib qolishi mumkin. Shuning uchun tasdiqlash majburiy:
    #: tekshirilmagan validator bilan hack oqimini ochib bo'lmaydi.
    #: `null` — hali tasdiqlanmagan (nashr darvozasi shuni ko'radi).
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"validator · {self.problem.slug}"


class ReferenceSolution(UpdatedModel):
    """Etalon yechim — hack testining javobini beradi ([ADR-0021]).

    Hacker kiritma yuboradi, himoyachining kodi shu kiritmada ishlaydi va
    chiqish NIMADIR bilan solishtirilishi kerak. O'sha «nimadir» —
    masalaning o'z to'g'ri yechimi bergan javob.

    ⚠️ Hackerning O'Z yechimi etalon bo'la olmaydi: u ataylab chekka
    holatda xato ishlaydigan kod bilan `AC` olib, keyin aynan o'sha
    holatni yuborsa, TO'G'RI ishlaydigan himoyachi «sindirilgan» bo'lib
    chiqardi. Shuning uchun etalon masala bilan keladi.

    Validator kabi u ham sandbox ICHIDA ishlaydi: kod bizniki, lekin
    kiritma ishonchsiz.

    [ADR-0021]: ../../../docs/07-adr/0021-hack-reference-solution.md
    """

    problem = models.OneToOneField(
        Problem, on_delete=models.CASCADE, related_name="reference_solution"
    )
    language = models.ForeignKey(
        Language, on_delete=models.PROTECT, related_name="reference_solutions"
    )
    source = models.TextField()

    def __str__(self) -> str:
        return f"etalon · {self.problem.slug}"


class Favourite(CreatedModel):
    """Keyinroq qaytish uchun belgilangan masala.

    RoboContest va Codeforces'dagi «sevimlilar» — uzun arxivda yo'qolib
    ketmaslikning eng oddiy usuli.
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="favourites")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="favourites")

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="uniq_favourite")
        ]
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.problem.slug}"


class ProblemVote(CreatedModel):
    """Masalaga «yoqdi / yoqmadi» ovozi.

    Yulduzli bahodan (`ProblemRating`) ALOHIDA: yulduz masalaning
    sifatini o'lchaydi va o'ylashni talab qiladi, ovoz esa bir bosish —
    shu sababli u ancha ko'p yig'iladi va boshqa savolga javob beradi.
    Import qilingan sanoqlar `Problem.likes_count` da, bular esa
    bizniki; ko'rsatishda qo'shiladi.
    """

    UP = 1
    DOWN = -1

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="problem_votes")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="votes")
    value = models.SmallIntegerField(choices=[(UP, "Yoqdi"), (DOWN, "Yoqmadi")])

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="uniq_problem_vote")
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug}: {self.value:+d}"


class EditorialUnlock(CreatedModel):
    """Yechim tahliliga kirish huquqi — ADR-0013.

    Yozuv FAQAT Qvant sarflab ochganda paydo bo'ladi. Masalani yechgan
    odamga tahlil baribir ochiq, unga yozuv kerak emas — aks holda
    yechganlar soni qadar keraksiz qator yig'ilardi.
    """

    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="editorial_unlocks"
    )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="unlocks")
    price = models.PositiveIntegerField()

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="uniq_editorial_unlock")
        ]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.problem.slug}"


class ProblemRating(TimeStampedModel):
    """Foydalanuvchining masalaga bergan bahosi (1–5).

    RoboContest sahifada «3.2 · 10 baholar» ko'rsatadi — muallif uchun
    ham, tanlayotgan solver uchun ham signal.
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="problem_ratings")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "problem"], name="uniq_problem_rating")
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug}: {self.score}"


class ProblemReport(models.Model):
    """Masaladagi nuqson haqida xabar.

    2089 masala tashqi arxivdan ko'chirilgan: bir qismida test yo'q,
    matnda formatlash buzilgan bo'lishi yoki tarjima xato bo'lishi
    mumkin. Ularning hammasini o'zimiz topib chiqa olmaymiz — yechayotgan
    odam esa darhol ko'radi. Xabar yo'li bo'lmasa, u nuqson bilan birga
    yo'qoladi.
    """

    class Reason(models.TextChoices):
        STATEMENT = "statement", "Matnda xato"
        TESTS = "tests", "Testlar noto'g'ri"
        TRANSLATION = "translation", "Tarjima xato"
        DUPLICATE = "duplicate", "Takroriy masala"
        OTHER = "other", "Boshqa"

    class Status(models.TextChoices):
        OPEN = "open", "Ochiq"
        ACCEPTED = "accepted", "Qabul qilindi"
        REJECTED = "rejected", "Rad etildi"

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="problem_reports")
    reason = models.CharField(max_length=16, choices=Reason.choices)
    comment = models.TextField(blank=True, max_length=2000)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            # Bir odam bir masala haqida bir marta ochiq xabar qoldiradi —
            # aks holda tugmani takror bosish navbatni to'ldirardi.
            models.UniqueConstraint(
                fields=["user", "problem"],
                condition=models.Q(status="open"),
                name="uniq_open_problem_report",
            )
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug}: {self.reason} ({self.status})"


# ── Judge muhiti va kalibrlash — PROMPT_0 §5 ──────────────────────────


class JudgeEnvironment(TimeStampedModel):
    """Yechim qaysi judge muhitida o'lchanganini bildiradi.

    Limitlar «muallif kompyuterida» tanlanmasligi kerak: judge serverining
    apparati, kompilyator versiyasi va sandbox sozlamasi natijaga ta'sir
    qiladi. Shuning uchun har bir revision qaysi muhitda kalibrlanganini
    biladi — qayta judge qilinganda natijalar qaysi sharoitda olinganini
    aniqlash mumkin bo'ladi.
    """

    key = models.CharField(max_length=64, unique=True)
    version = models.CharField(max_length=32)
    image = models.CharField(max_length=200, blank=True)
    architecture = models.CharField(max_length=32, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering: ClassVar = ["key"]
        verbose_name_plural = "judge environments"

    def __str__(self) -> str:
        return f"{self.key} ({self.version})"


class LimitCalibration(TimeStampedModel):
    """Bitta revision uchun limit o'lchovi — xom natija va yakuniy qaror.

    Limit shunchaki qo'lda yozilgan son bo'lib qolmasligi kerak (§5):
    etalon yechim vakillik testlarida yurgiziladi, xom o'lchov saqlanadi,
    keyin xavfsizlik koeffitsienti qo'llanib yakuniy limit chiqadi. Ya'ni
    «nega 2 sekund?» degan savolga javob bazada turadi, xotirada emas.
    """

    revision = models.ForeignKey(
        "problems.ProblemRevision", on_delete=models.CASCADE, related_name="calibrations"
    )
    language = models.ForeignKey(Language, null=True, blank=True, on_delete=models.SET_NULL)
    #: Xom o'lchovlar: `{"wall_ms": ..., "peak_kb": ..., "tests": n}`.
    measurements = models.JSONField(default=dict)
    safety_factor = models.FloatField(default=2.0)
    time_limit_ms = models.PositiveIntegerField()
    memory_limit_kb = models.PositiveIntegerField()
    measured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-measured_at"]

    def __str__(self) -> str:
        return f"{self.revision} {self.time_limit_ms}ms/{self.memory_limit_kb}kb"


# ── Yechim rollari — PROMPT_0 §4 ──────────────────────────────────────


class SolutionRole(models.TextChoices):
    """Yechim NIMA UCHUN yozilgani.

    Etalon yagona artefakt emas, **to'g'rilik dalili**: brute-force bilan
    differensial solishtirish, alternativa bilan mustaqil tekshirish,
    ataylab xato yechim bilan testlarning kuchini o'lchash. Shuning uchun
    rol — yechimning ajralmas qismi, izoh emas.
    """

    REFERENCE = "reference", "Etalon"
    BRUTE_FORCE = "brute_force", "Brute-force"
    ALTERNATIVE = "alternative", "Alternativa"
    SLOW = "slow", "Sekin (TLE kutiladi)"
    WRONG = "wrong", "Xato (WA kutiladi)"


class ProblemSolution(TimeStampedModel):
    """Rol bilan belgilangan yechim (ADR 0052).

    `ReferenceSolution` — bu modelning `role=reference` holati. U saqlanadi:
    hack oqimi va readiness harness'i unga tayanadi, ya'ni uni ko'chirish
    ishlayotgan yo'lni buzardi. Ikkisi bir xil artefaktning ikki ko'rinishi
    emas — `ReferenceSolution` MANBA, bu esa TO'PLAM: bitta masalada bir
    nechta rol bo'lishi mumkin.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="solutions")
    role = models.CharField(max_length=16, choices=SolutionRole.choices)
    language = models.ForeignKey(Language, null=True, blank=True, on_delete=models.SET_NULL)
    source = models.TextField(blank=True)
    #: Rol bo'yicha KUTILGAN natija. `wrong`/`slow` uchun dalil shu maydonsiz
    #: ma'nosiz: «xato yechim xato bo'ldi» hech narsani isbotlamaydi,
    #: «aynan shu testda WA bo'ldi» isbotlaydi.
    expected_verdict = models.CharField(max_length=8, blank=True)
    #: `wrong`/`slow` qaysi test guruhida yiqilishi kutiladi.
    target_group = models.CharField(max_length=16, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering: ClassVar = ["role", "pk"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem", "role"], name="uniq_solution_role"),
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug}:{self.role}"


# ── Versiyalangan masala paketi — PROMPT_0 §10 ────────────────────────


class RevisionStatus(models.TextChoices):
    DRAFT = "draft", "Qoralama"
    VALIDATING = "validating", "Tekshirilmoqda"
    READY = "ready", "Tayyor"
    FROZEN = "frozen", "Muzlatilgan"
    PUBLISHED = "published", "Nashr qilingan"
    DEPRECATED = "deprecated", "Eskirgan"


class ProblemRevision(TimeStampedModel):
    """Masala paketining MUZLATILGAN surati (ADR 0052).

    ⚠️ `Problem.readiness` bilan aralashtirmang — ular ORTOGONAL:

      `readiness`  — kontent sifati: S1–S4 bajarilganmi? Bitta ishchi nusxa
                     ustida ishlaydi va o'zgarib turadi.
      `ProblemRevision` — qaysi test/checker/limit bilan NASHR qilingan?
                     Muzlatilgandan keyin O'ZGARMAYDI.

    Kanonik oqim bitta: `readiness=VALIDATED` → revision freeze → publish.
    Ya'ni yangi qatlam mavjud lifecycle'ni KENGAYTIRADI, uning o'rnini
    bosmaydi va parallel state machine yaratmaydi.
    """

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="revisions")
    version = models.PositiveIntegerField()
    status = models.CharField(
        max_length=12, choices=RevisionStatus.choices, default=RevisionStatus.DRAFT
    )
    #: Butun paket surati: statement, testlar, limitlar, checker, validator,
    #: interactor, editorial, yechimlar. JSON — revision yaxlit o'qiladi,
    #: alohida so'rovlar uchun emas; test matni S3 da qoladi.
    package = models.JSONField(default=dict)
    #: `package` ning SHA-256 i — muzlatish paytida yoziladi. Keyinchalik
    #: artefakt o'zgarsa, mismatch shu yerda aniqlanadi.
    package_hash = models.CharField(max_length=64, blank=True)
    judge_environment = models.ForeignKey(
        JudgeEnvironment, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_by = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.SET_NULL)
    frozen_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    #: Nega bu revision nashr qilinmagan — oxirgi tekshiruv natijasi.
    gate_report = models.JSONField(default=list, blank=True)

    class Meta:
        ordering: ClassVar = ["problem", "-version"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["problem", "version"], name="uniq_revision_version"),
        ]

    def __str__(self) -> str:
        return f"{self.problem.slug} r{self.version} ({self.status})"

    #: Muzlatilgandan keyin paket o'zgarmaydi.
    FROZEN_STATUSES: ClassVar = frozenset({RevisionStatus.FROZEN, RevisionStatus.PUBLISHED})

    @property
    def is_frozen(self) -> bool:
        return self.status in self.FROZEN_STATUSES
