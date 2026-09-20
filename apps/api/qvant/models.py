"""Qvant iqtisodiyoti — 05-domain-model 🔒 va ADR-0002.

Asosiy qoida: **balans hech qachon to'g'ridan-to'g'ri yozilmaydi.**
Haqiqat manbai — `QvantTransaction` ledgeri; `QvantWallet.balance` esa kesh.
Shu sabab rejudge da qaytarish ham, audit ham mumkin bo'ladi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.bases import UpdatedModel

#: ADR-0002 anti-farm: kunlik maksimal emissiya.
#: Streak yutuqlari bundan TASHQARI (ular kamdan-kam va rejalashtirilgan).
DAILY_EARN_CAP = 100


class QvantWallet(UpdatedModel):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="wallet")
    balance = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user_id}: {self.balance} Qvant"


class QvantTransaction(models.Model):
    """Ledger — o'zgarmas yozuv. O'chirilmaydi, tuzatilmaydi."""

    class Reason(models.TextChoices):
        QUEST = "quest", "Quest"
        STREAK = "streak", "Streak yutug'i"
        CONTEST = "contest", "Musobaqa"
        PURCHASE = "purchase", "Xarid"
        REFUND = "refund", "Qaytarish"
        ADMIN = "admin", "Admin"
        QUIZ = "quiz", "Test"
        ARENA = "arena", "Arena"
        DUEL = "duel", "Duel"
        ACHIEVEMENT = "achievement", "Yutuq"
        #: Amaliyot siyosatidagi muvaffaqiyatli hack (ADR-0020).
        #: Kunlik shift ledgerda — farm qilib bo'lmaydi.
        HACK = "hack", "Hack"

    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="qvant_transactions"
    )
    amount = models.IntegerField(help_text="Musbat = topildi, manfiy = sarflandi")
    reason = models.CharField(max_length=16, choices=Reason.choices)
    ref_type = models.CharField(max_length=24, blank=True)
    ref_id = models.CharField(max_length=64, blank=True)
    balance_after = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["user", "-created_at"], name="qvant_tx_feed"),
            # Kunlik emissiya shiftini hisoblash uchun
            models.Index(fields=["user", "reason", "created_at"], name="qvant_tx_cap"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} {self.amount:+d} ({self.reason})"


class QvantQuest(models.Model):
    """Vazifa ta'rifi. Kodlar `qvant.quests` da hodisalarga bog'lanadi."""

    class Type(models.TextChoices):
        DAILY = "daily", "Kunlik"
        WEEKLY = "weekly", "Haftalik"
        ACHIEVEMENT = "achievement", "Yutuq"

    code = models.SlugField(unique=True)
    type = models.CharField(max_length=12, choices=Type.choices)
    title_uz = models.CharField(max_length=120)
    title_ru = models.CharField(max_length=120, blank=True)
    title_en = models.CharField(max_length=120, blank=True)
    reward = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering: ClassVar = ["type", "code"]

    def __str__(self) -> str:
        return f"{self.code} (+{self.reward})"


class UserQuestCompletion(models.Model):
    """Anti-farm kaliti — `period_key`.

    Kunlik quest uchun `period_key` = sana (`2026-09-06`), haftalik uchun
    ISO hafta (`2026-W36`), yutuq uchun bosqich (`streak-30`). Uniq cheklov
    bir davrda bir marta mukofot berilishini KAFOLATLAYDI — tekshiruv
    kodda emas, bazada.
    """

    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="quest_completions"
    )
    quest = models.ForeignKey(QvantQuest, on_delete=models.CASCADE, related_name="completions")
    period_key = models.CharField(max_length=24)
    awarded = models.PositiveIntegerField()
    completed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-completed_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(
                fields=["user", "quest", "period_key"], name="uniq_quest_period"
            )
        ]
        indexes: ClassVar = [
            # Activity reyting 30 kunlik oynada shu jadvaldan sanaydi
            models.Index(fields=["user", "-completed_at"], name="quest_activity_window")
        ]

    def __str__(self) -> str:
        return f"{self.user_id} {self.quest_id} {self.period_key}"


class ShopItem(models.Model):
    """ADR-0002: v1 da FAQAT kosmetika va qulaylik.

    Kontent ochish, funksiya ochish va obuna chegirmasi ataylab yo'q —
    ular alohida ADR talab qiladi.
    """

    class Category(models.TextChoices):
        STREAK_FREEZE = "streak_freeze", "Streak freeze"
        AVATAR_FRAME = "avatar_frame", "Avatar ramka"
        PROFILE_COVER = "profile_cover", "Profil cover"
        USERNAME_BADGE = "username_badge", "Username badge"

    code = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    title_uz = models.CharField(max_length=120)
    title_ru = models.CharField(max_length=120, blank=True)
    title_en = models.CharField(max_length=120, blank=True)
    price = models.PositiveIntegerField()
    asset_ref = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    #: Takroriy sotib olinadimi (streak freeze — ha, ramka — yo'q)
    is_consumable = models.BooleanField(default=False)

    class Meta:
        ordering: ClassVar = ["price", "code"]

    def __str__(self) -> str:
        return f"{self.code} ({self.price} Qvant)"


class UserInventory(models.Model):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="inventory")
    item = models.ForeignKey(ShopItem, on_delete=models.PROTECT, related_name="owners")
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_equipped = models.BooleanField(default=False)

    class Meta:
        ordering: ClassVar = ["-purchased_at"]
        indexes: ClassVar = [models.Index(fields=["user", "item"], name="inventory_lookup")]

    def __str__(self) -> str:
        return f"{self.user_id} — {self.item_id}"
