"""Model bazalari — vaqt tamg'alari uchun yagona manba.

Qaror (2026-09-20): abstrakt bazalar kiritiladi, **sxema o'zgarmaydi**.
Shu sabab bu faylda faqat MAVJUD shakllar takrorlanadi — yangi ustun
qo'shilmaydi va indeks o'zgartirilmaydi.

⚠️ Nega `core/mixins.py` ga qo'shilmadi: o'sha fayl «maydon qo'shmaydigan»
mixinlar uchun (`TimeWindowMixin`). Bu yerdagilar esa aynan **maydon**
qo'shadi, ya'ni ular model. Aralashtirilsa `Meta` merosi va
`mypy_django_plugin` chalkashadi.

Uch shakl (o'lchandi 2026-09-20, jami 45 model):

| Baza               | Maydonlar                  | Model |
|--------------------|----------------------------|-------|
| `CreatedModel`     | `created_at`               | 23    |
| `TimeStampedModel` | `created_at`, `updated_at` | 8     |
| `UpdatedModel`     | `updated_at`               | 5     |

⚠️ Qolgan 9 model bu bazalarga KIRMAYDI — ularda `created_at`
`db_index=True` bilan e'lon qilingan:

    core.EmailDelivery, core.EmailVerifyToken, core.PasswordResetToken,
    judging.Attempt, notifications.Notification, problems.ProblemReport,
    profiles.Follow, qvant.QvantTransaction, hacks.Hack

Indeksni birxillashtirish — **qo'shadigan DDL**, ya'ni alohida qaror
(qarang: xotirada `topics/07-django-drf.md`, leaderboard indeksi).
O'sha qaror qabul qilinmaguncha ular qo'lda yozilgan holida qoladi.

⚠️ Yangi model yozganda `created_at`/`updated_at` ni qo'lda yozmang —
shaklga mos bazani tanlang. Shakl mos kelmasa, bu indeks qarori.
"""

from __future__ import annotations

from django.db import models


class CreatedModel(models.Model):
    """Faqat yaratilish vaqti — 23 model."""

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Yaratilish va o'zgarish vaqti — 8 model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UpdatedModel(models.Model):
    """Faqat o'zgarish vaqti — 5 model.

    ⚠️ `created_at` YO'Q — bu mavjud holat, niyat emas: bu modellarda
    yaratilish vaqti hech qachon saqlanmagan. Ustun qo'shish DDL bo'lgani
    uchun hozircha o'zgartirilmaydi, lekin shakl shu yerda
    hujjatlashtirilgan — kelajakda bitta joydan tuzatiladi.
    """

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


__all__ = ["CreatedModel", "TimeStampedModel", "UpdatedModel"]
