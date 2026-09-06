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


class Article(models.Model):
    """O'quv maqolasi. Masalalarga bog'lanadi."""

    slug = models.SlugField(unique=True, max_length=120)
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["difficulty", "slug"]
        indexes: ClassVar = [
            models.Index(fields=["is_published", "difficulty"], name="article_browse")
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
    """O'quv yo'li — maqola va masalalarning tartiblangan ketma-ketligi."""

    slug = models.SlugField(unique=True, max_length=120)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    locale = models.CharField(max_length=2, default="uz")
    is_published = models.BooleanField(default=False, db_index=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "slug"]

    def __str__(self) -> str:
        return self.slug


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
            raise ValidationError("Qadamda maqola yoki masala bo'lishi kerak")
