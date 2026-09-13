"""Updates xizmat qatlami.

O'qilmagan holat `UpdateRead` orqali hisoblanadi. Yozuv faqat o'qilganda
yaratiladi (models.py izohiga qarang), shuning uchun "o'qilmagan" —
`published` minus `UpdateRead`.
"""

from __future__ import annotations

from django.db.models import Count, QuerySet
from django.utils import timezone

from core.models import User
from updates.models import SystemUpdate, UpdateRead


def published() -> QuerySet[SystemUpdate]:
    """Ochiq lenta — nashr etilgan va feature flag o'chirilmagan.

    `is_enabled` — rollback tugmasi (qaror 17-savol): o'chirilsa yozuv
    ko'rinmaydi, lekin bazada qoladi va arxivda saqlanadi.
    """
    return SystemUpdate.objects.filter(
        status=SystemUpdate.Status.PUBLISHED, is_enabled=True
    ).prefetch_related("translations")


def retrievable() -> QuerySet[SystemUpdate]:
    """Batafsil sahifa uchun — nashrdan olingan yozuv ham ochiladi.

    Qaror 20-savol: nashrdan olish — o'chirish EMAS, havola
    sindirilmaydi. Telegram kanal va Codeforces blogdagi e'lonlar shu
    havolaga ishora qiladi, ya'ni 404 bo'lsa tashqi havola o'ladi.

    Ikki istisno ATAYLAB:
      * `draft` — tasdiqlanmagan yozuv ochiq o'qilmaydi (qaror 15-savol);
      * `is_enabled=False` — modul darajasidagi rollback hamma joyda
        yopadi, chunki u "butun modul o'chirildi" degani.
    """
    return SystemUpdate.objects.filter(
        status__in=[SystemUpdate.Status.PUBLISHED, SystemUpdate.Status.WITHDRAWN],
        is_enabled=True,
    ).prefetch_related("translations")


def unread_queryset(user: User) -> QuerySet[SystemUpdate]:
    return published().exclude(reads__user=user)


def unread_count(user: User) -> int:
    return unread_queryset(user).count()


def unread_by_module(user: User) -> list[dict[str, object]]:
    """Nav chipi uchun: `[{"module": "problems", "count": 3}, …]`.

    Faqat noldan katta bo'lganlar qaytadi — chip ko'rsatilmasin.
    """
    rows = (
        unread_queryset(user)
        .values("module")
        .annotate(count=Count("id"))
        .filter(count__gt=0)
        .order_by("-count")
    )
    return [{"module": r["module"], "count": r["count"]} for r in rows]


def mark_read(user: User, ids: list[int] | None = None) -> int:
    """O'qilgan deb belgilash. `ids=None` — hammasi.

    `ignore_conflicts` — ikki marta bosilsa (yoki ikki qurilmada) xato
    chiqmasin; takroriy yozuv shunchaki o'tkazib yuboriladi.
    """
    qs = unread_queryset(user)
    if ids is not None:
        qs = qs.filter(pk__in=ids)
    rows = [UpdateRead(user=user, update=u) for u in qs.only("pk")]
    if not rows:
        return 0
    created = UpdateRead.objects.bulk_create(rows, ignore_conflicts=True, batch_size=500)
    return len(created)


def actionable_unread(user: User) -> QuerySet[SystemUpdate]:
    """Harakatga chaqiruvchi o'qilmaganlar (buzuvchi / olib tashlanadi).

    UI bularni doim ko'rsatadi — yashirib bo'lmaydi.
    """
    return unread_queryset(user).filter(kind__in=SystemUpdate.ACTIONABLE)


def prune_reads(update: SystemUpdate) -> int:
    """Nashrdan olingan yozuvning o'qilgan belgilarini tozalash.

    Yozuv arxivda qoladi (havola sindirilmaydi), lekin "o'qilmagan" deb
    turmasligi kerak — u endi lentada ko'rinmaydi.
    """
    if update.status == SystemUpdate.Status.PUBLISHED and update.is_enabled:
        return 0
    return UpdateRead.objects.filter(update=update).delete()[0]


def mark_published(update: SystemUpdate) -> SystemUpdate:
    update.status = SystemUpdate.Status.PUBLISHED
    if update.published_at is None:
        update.published_at = timezone.now()
    update.save(update_fields=["status", "published_at", "updated_at"])
    return update


def withdraw(update: SystemUpdate) -> SystemUpdate:
    """Nashrdan olish — o'chirish EMAS (qaror 20-savol).

    Yozuv arxivda qoladi va havolasi ishlaydi; faqat lentada ko'rinmaydi.
    """
    update.status = SystemUpdate.Status.WITHDRAWN
    update.save(update_fields=["status", "updated_at"])
    prune_reads(update)
    return update


def unread_counts_for(users: QuerySet[User]) -> dict[int, int]:
    """Bir necha foydalanuvchi uchun o'qilmaganlar soni — bitta so'rovda.

    `published()` sonidan `UpdateRead` sonini ayiradi. Har foydalanuvchi
    uchun alohida so'rov yuborilsa N+1 bo'lardi.
    """
    total = total_published()
    read = dict(
        UpdateRead.objects.filter(user__in=users).values_list("user_id").annotate(c=Count("id"))
    )
    return {uid: total - read.get(uid, 0) for uid in users.values_list("pk", flat=True)}


def total_published() -> int:
    return published().count()


def has_unread_actionable(user: User) -> bool:
    return actionable_unread(user).exists()


__all__ = [
    "actionable_unread",
    "has_unread_actionable",
    "mark_published",
    "mark_read",
    "prune_reads",
    "published",
    "retrievable",
    "total_published",
    "unread_by_module",
    "unread_count",
    "unread_counts_for",
    "unread_queryset",
    "withdraw",
]
