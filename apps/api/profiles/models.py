"""Foydalanuvchi profili: ko'nikma, texnologiya, karyera, tashqi profil,
obuna va jamoa.

`core.User` ga faqat bitta qiymatli maydonlar qo'shildi (mamlakat, maktab,
tug'ilgan sana…). Bitta odamda bir nechta bo'ladigan narsa — ko'nikma,
ta'lim joyi, jamoa — alohida jadvalda turadi.
"""

from __future__ import annotations

import secrets
from typing import ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from core.bases import CreatedModel


class Skill(models.Model):
    slug = models.SlugField(unique=True)
    name_uz = models.CharField(max_length=80)
    name_ru = models.CharField(max_length=80, blank=True)
    name_en = models.CharField(max_length=80, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "slug"]

    def __str__(self) -> str:
        return self.slug


class UserSkill(models.Model):
    """O'zini-o'zi baholash, KEP kabi — foydalanuvchi shunday tanladi.

    Daraja faqat ko'rsatkich: reytingga ham, tavsiyaga ham ta'sir qilmaydi.
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="users")
    level = models.PositiveSmallIntegerField(default=50, validators=[MaxValueValidator(100)])
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "id"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "skill"], name="uniq_user_skill"),
            models.CheckConstraint(condition=Q(level__lte=100), name="user_skill_level_max"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.skill_id}={self.level}"


class UserTechnology(models.Model):
    """`slug` — `profiles.catalog.TECHNOLOGIES` dagi kalit."""

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="technologies")
    slug = models.CharField(max_length=40)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "id"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "slug"], name="uniq_user_technology"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.slug}"


#: KEP-uslubidagi ko'nikma nishonlari — matn, ikonka, rang. Max 10.
MAX_SKILL_BADGES = 10
BADGE_TEXT_MAX = 24
BADGE_COLOR = r"^#[0-9A-Fa-f]{6}$"


class UserSkillBadge(models.Model):
    """Profil nishoni: erkin matn + katalog ikonkasi + rang."""

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="skill_badges")
    text = models.CharField(max_length=BADGE_TEXT_MAX)
    #: `profiles.catalog.TECHNOLOGIES` kaliti — frontend `TECH_ICONS` shu slug.
    icon = models.CharField(max_length=40)
    color = models.CharField(max_length=7, default="#4f46e5")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.text}"


class Education(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="educations")
    organization = models.CharField(max_length=150)
    degree = models.CharField(max_length=100, blank=True)
    start_year = models.PositiveSmallIntegerField(null=True, blank=True)
    start_month = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    #: Bo'sh — hozir ham shu yerda (`current=True` yoki `end_year` yo'q).
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_month = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    current = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.organization}"


class WorkExperience(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="work_experiences")
    company = models.CharField(max_length=150)
    title = models.CharField(max_length=100, blank=True)
    start_year = models.PositiveSmallIntegerField(null=True, blank=True)
    start_month = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    #: Bo'sh — hozir ham shu yerda (`current=True` yoki `end_year` yo'q).
    end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    end_month = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    current = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering: ClassVar = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.company}"


class ExternalProfile(models.Model):
    """Boshqa platformadagi profil. Reyting ochiq API'dan olinadi va keshlanadi.

    Egalik TEKSHIRILMAYDI — xuddi KEP'dagi kabi, bu shunchaki havola. Shu
    sababli reyting profilda «o'zi ko'rsatgan» deb emas, manba nomi bilan
    chiqadi va hech qayerda bizning reytingga aralashmaydi.
    """

    class Kind(models.TextChoices):
        CODEFORCES = "codeforces", "Codeforces"
        ATCODER = "atcoder", "AtCoder"
        LEETCODE = "leetcode", "LeetCode"
        LINKEDIN = "linkedin", "LinkedIn"
        TELEGRAM = "telegram", "Telegram"
        GITHUB = "github", "GitHub"
        INSTAGRAM = "instagram", "Instagram"
        X = "x", "X"
        YOUTUBE = "youtube", "YouTube"
        KAGGLE = "kaggle", "Kaggle"
        BLOG = "blog", "Blog"

    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="external_profiles"
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    handle = models.CharField(max_length=200)
    rating = models.IntegerField(null=True, blank=True)
    max_rating = models.IntegerField(null=True, blank=True)
    rank = models.CharField(max_length=40, blank=True)
    fetched_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["kind"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "kind"], name="uniq_external_per_kind"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.kind}={self.handle}"


class Follow(models.Model):
    follower = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="following_links"
    )
    following = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="follower_links"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["follower", "following"], name="uniq_follow"),
            models.CheckConstraint(condition=~Q(follower=F("following")), name="no_self_follow"),
        ]

    def __str__(self) -> str:
        return f"{self.follower_id} → {self.following_id}"


class Team(CreatedModel):
    """Jamoa — a'zolar kod yoki havola bilan qo'shiladi."""

    #: ICPC jamoasi 3 kishi, lekin jamoa musobaqadan tashqarida ham
    #: (sinfdoshlar, to'garak) ishlatiladi — chegara kengroq.
    MAX_MEMBERS = 10

    name = models.CharField(max_length=60)
    created_by = models.ForeignKey(
        "core.User", on_delete=models.SET_NULL, null=True, related_name="created_teams"
    )
    join_code = models.CharField(max_length=24, unique=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def new_code() -> str:
        return secrets.token_urlsafe(9)


class TeamMember(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Egasi"
        MEMBER = "member", "A'zo"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="team_memberships")
    role = models.CharField(max_length=8, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["joined_at", "id"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["team", "user"], name="uniq_team_member"),
        ]

    def __str__(self) -> str:
        return f"{self.team_id}:{self.user_id} ({self.role})"


class UserAchievement(models.Model):
    """Qo'lga kiritilgan yutuq (ADR-0018) — noyoblik va bir martalik Qvant uchun."""

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="achievements")
    code = models.CharField(max_length=32)
    achieved_at = models.DateTimeField(default=timezone.now)
    #: Berilgan Qvant. Quest to'lagan yoki migratsiyada tiklangan yutuqda 0.
    awarded = models.PositiveIntegerField(default=0)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "code"], name="uniq_user_achievement"),
        ]
        indexes: ClassVar = [models.Index(fields=["code"], name="achievement_code")]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.code}"
