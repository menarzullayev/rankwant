"""Bildirishnomalar — PRD P1-4.

Bu shunchaki qulaylik emas: [ADR-0007](../../docs/07-adr/0007-skills-uses-current-difficulty.md)
masala qayta baholanganda foydalanuvchiga XABAR BERISHNI majburiy qilgan,
chunki reyting o'z harakatisiz o'zgaradi va sababi ko'rinmasa
principle #2 («reyting aniq») buziladi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        RATING_CHANGED = "rating_changed", "Reyting o'zgardi"
        PROBLEM_RERATED = "problem_rerated", "Masala qayta baholandi"
        CONTEST_RESULT = "contest_result", "Musobaqa natijasi"
        QUEST_AWARDED = "quest_awarded", "Vazifa bajarildi"
        STREAK_MILESTONE = "streak_milestone", "Streak yutug'i"
        DUEL = "duel", "Duel"
        #: Hack natijasi (ADR-0020) — ikkala tomonga ham: hacker natijani,
        #: himoyachi esa yechimi nega bekor qilinganini biladi.
        HACK = "hack", "Hack"
        SYSTEM = "system", "Tizim"

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=24, choices=Kind.choices)
    #: Foydalanuvchiga ko'rinadigan matn. Tarjima qilinmaydi — hodisa
    #: yuz berganda foydalanuvchi tilida yoziladi.
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    ref_type = models.CharField(max_length=24, blank=True)
    ref_id = models.CharField(max_length=64, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["user", "-created_at"], name="notif_feed"),
            # O'qilmaganlar sonini tez hisoblash uchun
            models.Index(fields=["user", "read_at"], name="notif_unread"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.title}"

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
