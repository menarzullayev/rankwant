"""O'z o'qish kontenti — PRD P2-5.

ADR-0005: `docs/07-adr/0005-content-strategy-own-content.md`

Bu differensiatorning texnik shakli: **maqola ↔ masala ↔ roadmap**.
cp.uz ga bog'liqlik yo'q — kontent bizniki, ADR-0005 qarori.

`blog.Post` dan farqi: u platforma yangiliklari, bu esa o'quv materiali —
masalalarga bog'lanadi va roadmap ichida ketma-ketlik hosil qiladi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils import timezone

from core.bases import TimeStampedModel


class Article(TimeStampedModel):
    """O'quv maqolasi. Masalalarga bog'lanadi."""

    class Kind(models.TextChoices):
        ARTICLE = "article", "Maqola"
        #: Algoritm ma'lumotnomasi — qisqa, formal, kod bilan (RoboContest «Algoritmlar»)
        ALGORITHM = "algorithm", "Algoritm"

    slug = models.SlugField(unique=True, max_length=120)
    kind = models.CharField(
        max_length=12, choices=Kind.choices, default=Kind.ARTICLE, db_index=True
    )
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(help_text="Markdown + LaTeX")
    locale = models.CharField(max_length=2, default="uz")

    topics = models.ManyToManyField("problems.Topic", blank=True, related_name="articles")
    #: Maqola qaysi daraja uchun — masala qiyinligi shkalasida (800–3500)
    difficulty = models.PositiveIntegerField(default=800)

    author = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="articles"
    )
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    reading_minutes = models.PositiveIntegerField(default=0)

    # ── Imported articles (ADR-0062: the cp.uz algorithms library) ──────
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Boshlang'ich"
        INTERMEDIATE = "intermediate", "O'rta"
        ADVANCED = "advanced", "Yuqori"

    class Review(models.TextChoices):
        #: Imported, the agent review has not finished: never published.
        PENDING = "pending", "Ko'rik kutilmoqda"
        #: Reviewed technically and linguistically; fixes are in the log.
        REVIEWED = "reviewed", "Ko'rikdan o'tgan"
        #: The review could not fix it: stays a draft (ADR-0062 § 2.3).
        DRAFT = "draft", "Qoralama"

    #: The library's section, as in the address `/algorithms/<category>/<slug>`.
    category = models.SlugField(max_length=40, blank=True, db_index=True)
    subcategory = models.CharField(max_length=120, blank=True)
    level = models.CharField(max_length=12, choices=Level.choices, blank=True)
    #: Position within the library (the source's own order).
    order = models.PositiveIntegerField(default=0)
    #: The short card text: the idea, the complexity, where it is used.
    idea = models.TextField(blank=True)
    complexity = models.CharField(max_length=300, blank=True)
    uses = models.TextField(blank=True)
    #: The source's id (`algebra--binary-exp`); blank on our own articles.
    source_ref = models.CharField(max_length=120, blank=True)
    #: The original the text is adapted from — shown as the attribution.
    source_title = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(max_length=300, blank=True)
    source_commit = models.CharField(max_length=40, blank=True)
    source_license = models.CharField(max_length=32, blank=True)
    #: The cp.uz commit the text came from, and the hash of the text as it
    #: was imported. A body whose hash differs was edited here, and a later
    #: import leaves it alone (ADR-0062 § 2.1).
    import_commit = models.CharField(max_length=40, blank=True)
    import_sha256 = models.CharField(max_length=64, blank=True)
    translator = models.CharField(max_length=120, blank=True)
    review_state = models.CharField(max_length=12, choices=Review.choices, blank=True)

    class Meta:
        ordering: ClassVar = ["difficulty", "slug"]
        indexes: ClassVar = [
            models.Index(fields=["is_published", "difficulty"], name="article_browse")
        ]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["source_ref"],
                condition=~models.Q(source_ref=""),
                name="uniq_article_source_ref",
            )
        ]

    def __str__(self) -> str:
        return self.slug

    def save(self, *args: object, **kwargs: object) -> None:
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        if not self.reading_minutes:
            # ~200 so'z/daqiqa — taxminiy, lekin bo'shdan yaxshiroq
            self.reading_minutes = max(1, len(self.body.split()) // 200)
        super().save(*args, **kwargs)  # type: ignore[arg-type]


class ArticleTranslation(models.Model):
    """An article in another language (ADR-0062 § 2.4).

    For the imported library this is the English cp-algorithms original the
    Uzbek text was translated from, under the same licence. A locale without
    a row reads the article in its own language.
    """

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="translations")
    locale = models.CharField(max_length=8)
    title = models.CharField(max_length=200)
    body = models.TextField()
    #: Hash of the body as imported; a different body was edited here.
    import_sha256 = models.CharField(max_length=64, blank=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["article", "locale"], name="uniq_article_translation")
        ]

    def __str__(self) -> str:
        return f"{self.article_id}:{self.locale}"


class ArticleExternalLink(models.Model):
    """A practice problem on another judge (ADR-0062 § 2.5).

    `key` is the judge-independent id (`content.exercise_keys`): a problem
    imported here later from the same source can be matched by it.
    """

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="external_links")
    platform = models.CharField(max_length=80, blank=True)
    title = models.CharField(max_length=300)
    url = models.URLField(max_length=500)
    key = models.CharField(max_length=200, db_index=True)
    note = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order"]

    def __str__(self) -> str:
        return self.key


class ArticleReview(models.Model):
    """One entry of an imported article's review log (ADR-0062 § 2.3).

    The licence asks to say what we changed; the log says it change by change.
    """

    class Stage(models.TextChoices):
        IMPORT = "import", "Import"
        MECHANICAL = "mechanical", "Kod va formulalar"
        TECHNICAL = "technical", "Texnik"
        LANGUAGE = "language", "Til"

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="reviews")
    at = models.DateTimeField()
    actor = models.CharField(max_length=120)
    stage = models.CharField(max_length=12, choices=Stage.choices)
    decision = models.CharField(max_length=16)
    notes = models.TextField(blank=True)
    content_sha256 = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering: ClassVar = ["at", "pk"]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["article", "at", "stage", "actor"], name="uniq_article_review_entry"
            )
        ]

    def __str__(self) -> str:
        return f"{self.article_id} {self.stage} {self.decision}"


class ArticleProblemLink(models.Model):
    """Maqola ↔ masala bog'lanishi — differensiatorning yadrosi.

    `role` bog'lanish MA'NOSINI saqlaydi: maqolani o'qib mashq qilish
    uchunmi, yoki masala yechilgandan keyin tushuntirish uchunmi.
    """

    class Role(models.TextChoices):
        PRACTICE = "practice", "Mashq uchun"
        EXAMPLE = "example", "Maqoladagi misol"
        EDITORIAL = "editorial", "Yechim tushuntirishi"

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="problem_links")
    problem = models.ForeignKey(
        "problems.Problem", on_delete=models.CASCADE, related_name="article_links"
    )
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.PRACTICE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["article", "problem", "role"], name="uniq_article_problem_role"
            )
        ]

    def __str__(self) -> str:
        return f"{self.article_id} ↔ {self.problem_id} ({self.role})"


class Roadmap(models.Model):
    """O'quv yo'li — maqola va masalalarning tartiblangan ketma-ketligi.

    A study plan (ADR-0060 § 2.4) groups its steps into sections and has a
    page of its own; one without sections is the plain list it always was.
    """

    class Track(models.TextChoices):
        GENERAL = "general", "Umumiy"
        OLYMPIAD = "olympiad", "Olimpiada"

    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    #: The language of `title` and `description`; three characters, as
    #: Karakalpak is `kaa`.
    locale = models.CharField(max_length=3, default="uz")
    #: The other languages: `{locale: {"title": ..., "description": ...}}`.
    #: A missing field falls back to the text above, as in ADR-0058.
    translations = models.JSONField(default=dict, blank=True)
    track = models.CharField(max_length=16, choices=Track.choices, default=Track.GENERAL)
    is_published = models.BooleanField(default=False, db_index=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "slug"]

    def __str__(self) -> str:
        return self.slug


class RoadmapSection(models.Model):
    """A chapter of a study plan (ADR-0060 § 2.4): its own page and progress."""

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="sections")
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    #: As `Roadmap.translations`, in the roadmap's language scheme.
    translations = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["roadmap", "order"], name="uniq_roadmap_section_order")
        ]

    def __str__(self) -> str:
        return f"{self.roadmap_id} §{self.order}"


class RoadmapStep(models.Model):
    """Roadmap qadami — maqola YOKI masala.

    Ikkalasi ham ixtiyoriy, lekin kamida bittasi bo'lishi kerak
    (`clean` tekshiradi): qadam bo'sh bo'lsa foydalanuvchiga
    ko'rsatadigan narsa qolmaydi.
    """

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)
    article = models.ForeignKey(
        Article, null=True, blank=True, on_delete=models.SET_NULL, related_name="roadmap_steps"
    )
    problem = models.ForeignKey(
        "problems.Problem",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roadmap_steps",
    )
    is_optional = models.BooleanField(default=False)
    #: The chapter the step is in; `None` in a plan without sections.
    section = models.ForeignKey(
        RoadmapSection, null=True, blank=True, on_delete=models.SET_NULL, related_name="steps"
    )

    class Meta:
        ordering: ClassVar = ["order"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["roadmap", "order"], name="uniq_roadmap_order")
        ]

    def __str__(self) -> str:
        return f"{self.roadmap_id} #{self.order}"

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.article_id is None and self.problem_id is None:
            raise ValidationError("A step must have an article or a problem")
