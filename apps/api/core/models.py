"""Core entitylar — 05-domain-model 🔒."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class User(AbstractUser):
    """Foydalanuvchi va uning 4 reytingi.

    4 reyting boshidanoq modellashtiriladi, UI da fazali ochiladi — ADR-0006.
    """

    class Locale(models.TextChoices):
        UZ = "uz", "O'zbekcha"
        RU = "ru", "Русский"
        EN = "en", "English"

    display_name = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    # ADR-0006 — formulalar: 04-prd § Reyting formulalari
    rating_skills = models.IntegerField(default=0, db_index=True)
    rating_contest = models.IntegerField(default=1400, db_index=True)
    rating_activity = models.IntegerField(default=0)
    rating_challenges = models.IntegerField(default=1400)

    # Elo volatilligi uchun — birinchi 6 rated contest
    rated_contest_count = models.PositiveIntegerField(default=0)

    locale = models.CharField(max_length=2, choices=Locale.choices, default=Locale.UZ)
    theme = models.CharField(max_length=16, default="system")

    streak_count = models.PositiveIntegerField(default=0)
    streak_freeze_until = models.DateField(null=True, blank=True)
    last_active_date = models.DateField(null=True, blank=True)

    class Meta(AbstractUser.Meta):  # type: ignore[name-defined,misc]
        indexes: ClassVar = [
            models.Index(fields=["-rating_skills"], name="user_skills_desc"),
            models.Index(fields=["-rating_contest"], name="user_contest_desc"),
        ]
        constraints: ClassVar = [
            # `Aziz` va `aziz` bir xil nom. Serializerdagi tekshiruv
            # parallel so'rovda o'tkazib yuborishi mumkin — kafolat
            # bazada bo'lishi shart.
            models.UniqueConstraint(Lower("username"), name="uniq_username_ci"),
        ]

    def __str__(self) -> str:
        return self.username


class ApiToken(models.Model):
    """Personal Access Token — ADR-0008.

    Ochiq token FAQAT bir marta, yaratilganda ko'rsatiladi; bazada
    SHA-256 hash saqlanadi.
    """

    PREFIX = "rw_"

    class Scope(models.TextChoices):
        READ = "read", "O'qish"
        SUBMIT = "submit", "Yechim yuborish"
        CONTEST_MANAGE = "contest:manage", "Contest boshqaruvi"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens")
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=16)
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    scopes = models.JSONField(default=list)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    MAX_ACTIVE_PER_USER = 10

    class Meta:
        indexes: ClassVar = [models.Index(fields=["user", "revoked_at"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.prefix}…)"

    @staticmethod
    def hash_token(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    @classmethod
    def issue(
        cls, user: User, name: str, scopes: list[str], expires_at: datetime
    ) -> tuple[ApiToken, str]:
        """Yangi token yaratadi. Qaytaradi: (obyekt, OCHIQ token).

        Ochiq token hech qayerda saqlanmaydi — chaqiruvchi uni bir marta
        foydalanuvchiga ko'rsatadi va unutadi.
        """
        raw = cls.PREFIX + secrets.token_urlsafe(32)
        token = cls.objects.create(
            user=user,
            name=name,
            prefix=raw[:10],
            token_hash=cls.hash_token(raw),
            scopes=scopes,
            expires_at=expires_at,
        )
        return token, raw

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > timezone.now()

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes
