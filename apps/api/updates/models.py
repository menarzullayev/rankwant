"""Platforma o'zgarishlari — Updates moduli.

Qaror sessiyasi: `rankwant-updates-design/DECISION-SESSION.md` (20 savol).

Bu modul `blog.Post` dan **ataylab ajratilgan**:

- `blog` — uzoq muharrir kontenti (yangilik, e'lon, muharrir maqolasi).
- `updates` — **changelog**: nima o'zgardi, qaysi turda, qaysi modulda.
  Manbasi GitHub, 10 turga tasniflanadi, tasdiq oqimidan o'tadi.

Ikkalasi bir joyga qo'yilsa filtr va UI chalkashadi (qaror: yangi app).

Uchta muhim qaror shu faylda:

1. **10 tur** — 9 va 10 (`breaking`, `deprecated`) foydalanuvchini
   HARAKATGA chaqiradi, qolgan 8 tasi faqat xabar beradi. Shuning uchun
   ular UI da alohida rang va joy oladi.
2. **Tarjima alohida jadvalda** — `blog`/`content` da har til alohida qator
   (`locale`), chunki u yerda har tarjima mustaqil maqola. Bu yerda esa
   **bitta o'zgarish, 10 til** — guruh kaliti kerak bo'lardi. Shuning uchun
   `SystemUpdateTranslation`.
3. **`status`** — qoralama → nashr → nashrdan olish. Nashrdan olingan yozuv
   **o'chirilmaydi**: havola sindirilmaydi (qaror 20-savol).
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models
from django.utils import timezone

#: Interfeys tillari — manba: `apps/web/src/i18n/locales/` (10 fayl).
#: Uchta ro'yxat bir xil bo'lishi shart: `User.Locale`, `settings.LANGUAGES`
#: va `core.email_text.LOCALES`. Ular `tools/check_locales_parity.py` bilan
#: CI da solishtiriladi — qo'lda takrorlanmaydi.
LOCALES: tuple[str, ...] = ("uz", "ru", "en", "kk", "ky", "tg", "tr", "es", "zh", "kaa")

#: Kanonik til — qolgan 9 tasi undan tarjima qilinadi.
SOURCE_LOCALE = "uz"


class SystemUpdate(models.Model):
    """Bitta o'zgarish. Kanonik matn — o'zbekcha; qolgan tillar tarjimada."""

    class Kind(models.TextChoices):
        # --- faqat xabar beradi (8 ta) ---
        NEW = "new", "Yangi"
        IMPROVED = "improved", "Yaxshilandi"
        FIXED = "fixed", "Tuzatildi"
        PERFORMANCE = "performance", "Tezlik"
        SECURITY = "security", "Xavfsizlik"
        DESIGN = "design", "Dizayn"
        CONTENT = "content", "Kontent"
        INFRASTRUCTURE = "infrastructure", "Infratuzilma"
        # --- harakatga chaqiradi (2 ta) — UI da alohida ---
        BREAKING = "breaking", "Buzuvchi"
        DEPRECATED = "deprecated", "Olib tashlanadi"

    #: Harakatga chaqiruvchi turlar. UI ularni ajratib ko'rsatadi.
    ACTIONABLE: ClassVar[frozenset[str]] = frozenset({"breaking", "deprecated"})

    class Module(models.TextChoices):
        PROBLEMS = "problems", "Masalalar"
        CONTESTS = "contests", "Musobaqalar"
        ARENA = "arena", "Bellashuvlar"
        JUDGE = "judge", "Tekshiruv"
        RATINGS = "ratings", "Reyting"
        QVANT = "qvant", "Qvant"
        PROFILE = "profile", "Profil"
        CLASSROOM = "classroom", "Sinf"
        QUIZZES = "quizzes", "Testlar"
        CONTENT = "content", "Kontent"
        DESIGN = "design", "Dizayn"
        CORE = "core", "Umumiy"

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        PUBLISHED = "published", "Nashr etilgan"
        WITHDRAWN = "withdrawn", "Nashrdan olingan"

    # --- kanonik kontent (o'zbekcha) ---
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, help_text="Markdown")
    locale = models.CharField(max_length=5, default=SOURCE_LOCALE)

    # --- tasnif ---
    kind = models.CharField(max_length=16, choices=Kind.choices, db_index=True)
    module = models.CharField(max_length=16, choices=Module.choices, db_index=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True
    )

    #: Semantik versiya — ixtiyoriy (`v1.4.0`). Bo'sh bo'lsa yozuv sanaga tayanadi.
    version = models.CharField(max_length=32, blank=True)

    # --- manba (GitHub) ---
    #: `owner/repo` — keyin boshqa repolar ham qo'shilishi mumkin.
    source_repo = models.CharField(max_length=120, blank=True)
    #: Commit SHA, PR raqami, release tegi — qoralama qayerdan kelgani.
    source_refs = models.JSONField(default=list, blank=True)
    #: GitHub havolasi — UI da "manbani ko'rish".
    source_url = models.URLField(blank=True)

    #: Rasm — faqat kerak bo'lganda (dizayn o'zgarishlari uchun skrinshot).
    image = models.URLField(blank=True)

    # --- sanalar ---
    #: O'zgarish chiqqan sana. `published_at` dan farq qiladi: yozuv
    #: kechroq yozilishi mumkin, lekin sana o'zgarishning haqiqiy sanasi.
    released_at = models.DateField(db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    #: Feature flag (qaror 17-savol) — o'chirilsa yozuv ko'rinmaydi,
    #: lekin bazada qoladi. Rollback bir tugma.
    is_enabled = models.BooleanField(default=True, db_index=True)

    #: Muallif — jamoa a'zosi (qaror 9-savol: faqat jamoa yozadi).
    author = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="updates"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar = ["-released_at", "-pk"]
        indexes: ClassVar = [
            # Ochiq lenta — eng ko'p ishlatiladigan so'rov
            models.Index(fields=["status", "is_enabled", "-released_at"], name="update_feed"),
            models.Index(fields=["module", "-released_at"], name="update_by_module"),
            models.Index(fields=["kind", "-released_at"], name="update_by_kind"),
        ]

    def __str__(self) -> str:
        return f"[{self.get_kind_display()}] {self.title}"

    def save(self, *args: object, **kwargs: object) -> None:
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)  # type: ignore[arg-type]

    @property
    def is_actionable(self) -> bool:
        """Foydalanuvchi biror narsa qilishi kerakmi (buzuvchi / olib tashlanadi)."""
        return self.kind in self.ACTIONABLE


class SystemUpdateTranslation(models.Model):
    """Bitta o'zgarishning boshqa tildagi matni.

    `SystemUpdate` dagi `title`/`body` — o'zbekcha kanonik. Qolgan 9 til
    shu jadvalda. Tarjima yo'q bo'lsa API kanonik matnni qaytaradi
    (bo'sh joy ko'rsatilmaydi).
    """

    update = models.ForeignKey(SystemUpdate, on_delete=models.CASCADE, related_name="translations")
    locale = models.CharField(max_length=5, db_index=True)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, help_text="Markdown")

    #: Mashina tarjimasi bo'lsa — belgilanadi. Foydalanuvchi bilishi kerak.
    is_machine = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["update", "locale"], name="uniq_update_locale"),
        ]
        ordering: ClassVar = ["locale"]

    def __str__(self) -> str:
        return f"{self.update_id}:{self.locale}"


class UpdateRead(models.Model):
    """Foydalanuvchi qaysi o'zgarishni o'qigan (qaror 7-savol).

    Bazada saqlanadi — brauzerda emas: qurilmalar orasida mos kelishi va
    keyingi fazalarda (ovoz, kuzatish, tavsiya) asos bo'lishi kerak.

    Yozuv **faqat o'qilganda** yaratiladi — oldindan hamma foydalanuvchi
    uchun qator yaratish 10 000 foydalanuvchi × 25 yozuv = 250 000 qator
    bo'lardi va ularning aksari hech qachon o'qilmaydi.
    """

    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="update_reads")
    update = models.ForeignKey(SystemUpdate, on_delete=models.CASCADE, related_name="reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["user", "update"], name="uniq_user_update_read"),
        ]
        indexes: ClassVar = [
            models.Index(fields=["user", "-read_at"], name="update_read_user"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}→{self.update_id}"
