"""Courses: Course -> Module -> Section -> Lesson (ADR-0056).

Owner decisions of 2026-11-10:

* four levels, lessons of four kinds: text, problem, quiz, video;
* one course, lessons in several languages: titles and bodies live in
  translation rows, one per locale, falling back to the course's base locale;
* access: free (signed-in users), Qvant, paid (one-time purchase or a plan),
  and a classroom can be given a course;
* progress per lesson, optional sequential unlock, a certificate after every
  required lesson plus the final quiz at or above the course threshold, Qvant
  rewards for finishing a module and the course;
* published only after staff review.

Other apps are referenced by string so that `courses` never imports their
models (`tools/check_architecture.py`).
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.bases import CreatedModel, TimeStampedModel

# Content locales, the same set as `CONTENT_NAME_LOCALES` on the web. A new
# language is a new value here, not a migration of every text column.
CONTENT_LOCALES = ("uz", "ru", "en")
LOCALE_CHOICES = [(code, code) for code in CONTENT_LOCALES]


class Course(TimeStampedModel):
    class Access(models.TextChoices):
        FREE = "free", "Free"
        QVANT = "qvant", "Qvant"
        PAID = "paid", "Paid"

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    slug = models.SlugField(unique=True, max_length=120)
    base_locale = models.CharField(max_length=2, choices=LOCALE_CHOICES, default="uz")
    level = models.CharField(max_length=12, choices=Level.choices, default=Level.BEGINNER)
    access = models.CharField(max_length=8, choices=Access.choices, default=Access.FREE)
    # Prices are set or changed only through staff review (ADR-0056 § 3.6).
    price_qvant = models.PositiveIntegerField(default=0)
    price_uzs = models.PositiveIntegerField(default=0, help_text="One-time price in UZS.")
    sequential = models.BooleanField(
        default=False, help_text="A lesson opens only after the previous required one is done."
    )
    certificate_threshold = models.PositiveSmallIntegerField(
        default=70,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Final quiz score, in percent, needed for the certificate.",
    )
    final_quiz = models.ForeignKey(
        "quizzes.Quiz",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="final_for_courses",
    )
    reward_qvant = models.PositiveIntegerField(
        default=0, help_text="Paid once when the course is completed."
    )
    cover_url = models.CharField(max_length=500, blank=True)
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="authored_courses"
    )
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    review_requested_at = models.DateTimeField(null=True, blank=True, db_index=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.slug

    def clean(self) -> None:
        if self.access == self.Access.QVANT and self.price_qvant <= 0:
            raise ValidationError({"price_qvant": "A Qvant course needs a Qvant price."})
        if self.access == self.Access.PAID and self.price_uzs <= 0:
            raise ValidationError({"price_uzs": "A paid course needs a price in UZS."})


class CourseTranslation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="translations")
    locale = models.CharField(max_length=2, choices=LOCALE_CHOICES)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True, help_text="Markdown + LaTeX")
    outcomes = models.TextField(
        blank=True, help_text="What the learner will be able to do; one per line."
    )
    requirements = models.TextField(blank=True, help_text="One per line.")
    audience = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "locale"], name="course_translation_once"),
        ]

    def __str__(self) -> str:
        return f"{self.course.slug}:{self.locale}"


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    order = models.PositiveIntegerField(default=0)
    reward_qvant = models.PositiveIntegerField(
        default=0, help_text="Paid once when the module is completed."
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.course.slug}/m{self.order}"


class ModuleTranslation(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="translations")
    locale = models.CharField(max_length=2, choices=LOCALE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["module", "locale"], name="module_translation_once"),
        ]

    def __str__(self) -> str:
        return f"{self.module}:{self.locale}"


class Section(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="sections")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.module}/s{self.order}"


class SectionTranslation(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="translations")
    locale = models.CharField(max_length=2, choices=LOCALE_CHOICES)
    title = models.CharField(max_length=200)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["section", "locale"], name="section_translation_once"),
        ]

    def __str__(self) -> str:
        return f"{self.section}:{self.locale}"


class Lesson(models.Model):
    class Kind(models.TextChoices):
        TEXT = "text", "Text"
        PROBLEM = "problem", "Problem"
        QUIZ = "quiz", "Quiz"
        VIDEO = "video", "Video"

    class VideoProvider(models.TextChoices):
        YOUTUBE = "youtube", "YouTube"
        VIMEO = "vimeo", "Vimeo"
        # Our own HLS in R2 (ADR-0056 § 3.5): the only provider allowed for
        # paid courses, because YouTube and Vimeo links can be shared.
        HLS = "hls", "HLS (R2)"

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    order = models.PositiveIntegerField(default=0)
    kind = models.CharField(max_length=8, choices=Kind.choices, default=Kind.TEXT)
    is_required = models.BooleanField(default=True)
    is_preview = models.BooleanField(
        default=False, help_text="Open to visitors who have not enrolled (never a paid video)."
    )
    problem = models.ForeignKey(
        "problems.Problem",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="course_lessons",
    )
    quiz = models.ForeignKey(
        "quizzes.Quiz",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="course_lessons",
    )
    quiz_pass_percent = models.PositiveSmallIntegerField(
        default=70, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    video_provider = models.CharField(max_length=8, choices=VideoProvider.choices, blank=True)
    # YouTube or Vimeo video id, or the R2 key prefix of the HLS rendition.
    video_ref = models.CharField(max_length=200, blank=True)
    video_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.section}/l{self.order}"

    def clean(self) -> None:
        errors: dict[str, str] = {}
        if self.kind == self.Kind.PROBLEM and self.problem_id is None:
            errors["problem"] = "A problem lesson needs a problem."
        if self.kind == self.Kind.QUIZ and self.quiz_id is None:
            errors["quiz"] = "A quiz lesson needs a quiz."
        if self.kind == self.Kind.VIDEO:
            if not self.video_provider or not self.video_ref:
                errors["video_ref"] = "A video lesson needs a provider and a video."
            course = self.section.module.course if self.section_id else None
            paid = course is not None and course.access == Course.Access.PAID
            if paid and self.video_provider != self.VideoProvider.HLS:
                errors["video_provider"] = "Paid courses serve video only from R2 (HLS)."
        if errors:
            raise ValidationError(errors)


class LessonTranslation(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="translations")
    locale = models.CharField(max_length=2, choices=LOCALE_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, help_text="Markdown + LaTeX")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["lesson", "locale"], name="lesson_translation_once"),
        ]

    def __str__(self) -> str:
        return f"{self.lesson}:{self.locale}"


class Enrollment(CreatedModel):
    class Source(models.TextChoices):
        FREE = "free", "Free"
        QVANT = "qvant", "Qvant"
        PURCHASE = "purchase", "Purchase"
        PLAN = "plan", "Plan"
        CLASSROOM = "classroom", "Classroom"
        STAFF = "staff", "Staff grant"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.FREE)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="enrollment_once"),
        ]


class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "lesson"], name="lesson_progress_once"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.lesson}"


class VideoAsset(CreatedModel):
    """A course's own video on R2 (or MinIO), as encrypted HLS (ADR-0056 § 3.5).

    Owner decisions of 2026-11-10: renditions up to the source's own height,
    the uploader picks which; segments are AES-128 encrypted and may be served
    from a public bucket, the key only through the API to readers the lesson
    is open to. A lesson may only point at an asset of its own course — a key
    typed by hand could otherwise reach another course's paid video.
    """

    class Status(models.TextChoices):
        UPLOADING = "uploading", "Uploading"
        QUEUED = "queued", "Queued"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    class Source(models.TextChoices):
        #: A video file, encoded here (owner decision: ffmpeg in a worker).
        FILE = "file", "Video file"
        #: A ready HLS folder in a zip, re-muxed and encrypted here.
        HLS_ZIP = "hls_zip", "HLS zip"

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="videos")
    #: Object key prefix in the video bucket, e.g. `v/4f1c…`; also the value
    #: a lesson keeps in `video_ref`.
    key = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PROCESSING)
    #: Rendition heights in pixels, ascending, e.g. `[360, 720, 1080]`.
    heights = models.JSONField(default=list, blank=True)
    seconds = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=8, choices=Source.choices, default=Source.FILE)
    #: What the uploader asked for; the encoder keeps the rungs at or below
    #: the source. Empty = every rung up to the source.
    requested_heights = models.JSONField(default=list, blank=True)
    #: Where the browser uploads the original, and the S3 multipart upload.
    source_key = models.CharField(max_length=128, blank=True)
    upload_id = models.CharField(max_length=256, blank=True)
    size = models.BigIntegerField(default=0)
    #: The AES-128 key of every segment. Never serialised; served only by
    #: the key endpoint, to readers the lesson is open to.
    aes_key = models.BinaryField(max_length=16, editable=False)
    error = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    def __str__(self) -> str:
        return f"{self.course.slug}:{self.key}"
