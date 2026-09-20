"""Platforma yo'l xaritasi — foydalanuvchi takliflari, ovozlar va izohlar.

Variant C ("Yo'l xaritasi"). Manba:
`docs/research/2026-09-13-rankwant-updates-design/DESIGN-VARIANTS.md`
va faza-3 qarorlari (izohlar bilan, ovoz o'zgartirsa bo'ladi, taklif ochiq
va ovoz yig'adi, alohida sahifa).

Modul `updates` (changelog) dan ATAYLAB ajratilgan:

- `updates` — **o'tmish**: nima chiqarildi, sana bilan, doimiy havola.
- `roadmap` — **kelajak**: nima rejalashtirilgan, ovoz bilan.

Ikkalasi bitta jadvalda bo'lsa "chiqarildi" ustuni changelog bilan
aralashib ketardi. Bog'lanish baribir bor: chiqarilgan band
`SystemUpdate` ga havola qiladi (`update` maydoni).

NOM: `roadmap` app deb ataladi, lekin URL prefiksi **`platform-roadmap`**.
Sabab: `content` app ida allaqachon `/roadmaps/` bor (ta'lim
traektoriyasi) va DRF router nomlari ham band (`roadmap`, `staff-roadmap`).
Bir harf farq qiladigan ikki manzil (`/roadmaps` va `/roadmap`) kodda ham,
havolada ham adashtiradi.

Uchta muhim qaror shu faylda:

1. **`suggested` — ochiq va ovoz yig'adi.** Taklif darhol ro'yxatda
   "Ko'rib chiqilmoqda" holatida ko'rinadi; jamoa keyin uni `planned` ga
   o'tkazadi yoki `declined` qiladi. Yopiq navbat tanlanmadi: odam ovozi
   ta'sir qilmayotganini ko'rib, taklif berishdan to'xtaydi.
2. **Ovoz — qatorning MAVJUDLIGI, qiymat emas.** `unique(item, user)`
   takroriy ovozni bazada taqiqlaydi; fikr o'zgarsa qator o'chiriladi
   (toggle). Ya'ni alohida `value` ustuni kerak emas va "bir odam bir
   ovoz" qoidasi ilova kodiga tayanmaydi.
3. **Muddat — CHORAK darajasida.** Aniq sana va'da qilinmaydi: bajarilmasa
   ishonch buziladi (Variant C ning asosiy kamchiligi). `target_quarter` —
   erkin yorliq ("2026-Q4", "Sentabr oxiri"), sana emas.

Holat tarixi alohida jadval EMAS: uchta o'tish vaqti (`planned_at`,
`started_at`, `released_at`) yetarli, ortiqcha yozuv yaratmaydi va
batafsil sahifadagi "holat tarixi" shulardan chiziladi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils import timezone

from core.bases import CreatedModel, TimeStampedModel


class RoadmapItem(TimeStampedModel):
    """Bitta reja bandi — taklif, reja yoki chiqarilgan ish."""

    class Status(models.TextChoices):
        #: Foydalanuvchi taklifi. Ochiq ko'rinadi va ovoz yig'adi.
        SUGGESTED = "suggested", "Ko'rib chiqilmoqda"
        PLANNED = "planned", "Rejalashtirilgan"
        IN_PROGRESS = "in_progress", "Ishlanmoqda"
        RELEASED = "released", "Chiqarildi"
        DECLINED = "declined", "Rad etilgan"

    #: Kanban ustunlari. `declined` ATAYLAB yo'q: rad etilganlar taxtani
    #: to'ldirib, "nima rejalashtirilgan" savolini xiralashtiradi. Ular
    #: filtrda va batafsil sahifada ko'rinadi — yashirilmaydi.
    COLUMNS: ClassVar[tuple[str, ...]] = (
        Status.SUGGESTED,
        Status.PLANNED,
        Status.IN_PROGRESS,
        Status.RELEASED,
    )

    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, help_text="Markdown")

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.SUGGESTED, db_index=True
    )

    #: Muddat — chorak darajasida, erkin yorliq. ANIQ SANA EMAS: bajarilmagan
    #: sana ishonchni buzadi, chorak esa kutilmagan kechikishni ko'taradi.
    target_quarter = models.CharField(max_length=24, blank=True)

    #: Muallif — taklif bergan foydalanuvchi. Jamoa yozgan bandda bo'sh.
    author = models.ForeignKey(
        "core.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roadmap_items",
    )

    #: Chiqarilganda bog'lanadigan changelog yozuvi. Havola shu orqali
    #: quriladi: "Chiqarildi" ustunidan `/updates/<id>` ga o'tiladi.
    update = models.ForeignKey(
        "updates.SystemUpdate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roadmap_items",
    )

    #: Holat tarixi — uchta o'tish vaqti. Alohida jadval emas.
    planned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)

    #: Feature flag (updates moduli bilan bir xil naqsh): o'chirilsa band
    #: ko'rinmaydi, lekin bazada va ovozlari bilan qoladi.
    is_enabled = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-created_at", "-pk"]
        indexes: ClassVar = [
            models.Index(fields=["status", "is_enabled", "-created_at"], name="roadmap_feed"),
        ]

    def __str__(self) -> str:
        return f"[{self.get_status_display()}] {self.title}"

    @property
    def is_open(self) -> bool:
        """Hali chiqarilmagan va rad etilmagan — ovoz berish mantiqan bor."""
        return self.status not in {self.Status.RELEASED, self.Status.DECLINED}

    def set_status(self, status: str) -> None:
        """Holatni o'zgartiradi va o'tish vaqtini yozadi.

        Vaqt faqat BIRINCHI marta yoziladi: band orqaga qaytarilib yana
        oldinga o'tkazilsa, "rejalashtirilgan sana" o'zgarmasligi kerak —
        aks holda tarix har tegilganda yangilanib, yolg'on ko'rsatardi.
        """
        now = timezone.now()
        self.status = status
        if status == self.Status.PLANNED and self.planned_at is None:
            self.planned_at = now
        if status == self.Status.IN_PROGRESS and self.started_at is None:
            self.started_at = now
        if status == self.Status.RELEASED and self.released_at is None:
            self.released_at = now
        self.save(
            update_fields=[
                "status",
                "planned_at",
                "started_at",
                "released_at",
                "updated_at",
            ]
        )


class RoadmapVote(CreatedModel):
    """Foydalanuvchining bitta bandga ovozi.

    Qatorning MAVJUDLIGI — ovoz. Qiymat ustuni yo'q: "bir odam bir ovoz"
    shartini `unique` bajaradi, fikr o'zgargani esa qatorni o'chirish.
    """

    item = models.ForeignKey(RoadmapItem, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="roadmap_votes")

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["item", "user"], name="uniq_roadmap_vote"),
        ]
        indexes: ClassVar = [
            models.Index(fields=["user", "-created_at"], name="roadmap_vote_user"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}→{self.item_id}"


class RoadmapComment(TimeStampedModel):
    """Band ostidagi izoh.

    Moderatsiya — **keyin** (post-moderation): izoh darhol ko'rinadi,
    jamoa kerak bo'lsa `is_hidden` qiladi. Oldindan tasdiq talab qilinsa
    muhokama sekinlashadi va jamoa har izohni kutib o'tirishi kerak
    bo'lardi — hozircha jamoa kichik.
    """

    item = models.ForeignKey(RoadmapItem, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "core.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roadmap_comments",
    )
    body = models.TextField()

    #: Yashirilgan izoh API dan chiqmaydi, lekin o'chirilmaydi — jamoa
    #: qarorini keyin ko'rib chiqishi mumkin.
    is_hidden = models.BooleanField(default=False, db_index=True)

    class Meta:
        # Eski izoh yuqorida — muhokama tartibi.
        ordering: ClassVar = ["created_at", "pk"]
        indexes: ClassVar = [
            models.Index(fields=["item", "is_hidden", "created_at"], name="roadmap_comment_feed"),
        ]

    def __str__(self) -> str:
        return f"{self.item_id}: {self.body[:40]}"
