"""Roadmap xizmat qatlami.

Hisob-kitob (ovoz soni, "men ovoz berdimmi", izoh soni) shu yerda —
view'da emas: bitta joyda bo'lsa ro'yxat ham, batafsil ham bir xil
qoidaga bo'ysunadi.
"""

from __future__ import annotations

from django.db.models import Count, Exists, OuterRef, Q, QuerySet

from core.models import User
from roadmap.models import RoadmapComment, RoadmapItem, RoadmapVote


def visible() -> QuerySet[RoadmapItem]:
    """Ommaviy ro'yxat — feature flag o'chirilmagan hamma band.

    `declined` ham kiradi: u yashirilmaydi. Rad etilgan taklifni
    ko'rsatish shaffoflik beradi va "taklif berdim, javob bo'lmadi"
    taassurotini yo'q qiladi — lekin kanbanda ustun egallamaydi.
    """
    return RoadmapItem.objects.filter(is_enabled=True)


def board() -> QuerySet[RoadmapItem]:
    """Kanban ustunlari — `declined` siz."""
    return visible().filter(status__in=RoadmapItem.COLUMNS)


def with_counts(queryset: QuerySet[RoadmapItem], user: User | None = None) -> QuerySet[RoadmapItem]:
    """Ovoz soni, izoh soni va "men ovoz berdimmi" — bitta so'rovda.

    ⚠️ `Count` ni `distinct=True` siz ikki marta qo'shib bo'lmaydi: ikki
    bog'lanish bir vaqtda qo'shilsa ular bir-birini ko'paytiradi
    (cartesian). O'lchandi — 3 ovoz va 2 izohli band ikkalasini ham
    `6` deb qaytargan edi. Shuning uchun har biri `distinct=True`.

    ⚠️ Annotatsiya nomi `vote_count`, `votes` EMAS: `votes` —
    `RoadmapVote.item` ning teskari bog'lanishi (`related_name="votes"`),
    ya'ni bir xil nom mypy'da `no-redef` beradi va qaysi biri
    ishlatilayotgani noaniq bo'lardi.
    """
    queryset = queryset.annotate(
        vote_count=Count("votes", distinct=True),
        comment_count=Count("comments", filter=Q(comments__is_hidden=False), distinct=True),
    )
    if user is not None and user.is_authenticated:
        queryset = queryset.annotate(
            has_voted=Exists(RoadmapVote.objects.filter(item=OuterRef("pk"), user=user))
        )
    return queryset


def set_vote(user: User, item: RoadmapItem, on: bool) -> tuple[bool, int]:
    """Ovoz qo'shadi yoki olib tashlaydi. Qaytaradi: `(ovoz berganmi, son)`.

    Ikki amal ham IDEMPOTENT: `get_or_create` va `filter().delete()`.
    Ya'ni ikki marta bosilsa yoki ikki qurilmadan bir vaqtda bosilsa
    xato chiqmaydi va son ikki marta o'zgarmaydi.
    """
    if on:
        RoadmapVote.objects.get_or_create(item=item, user=user)
    else:
        RoadmapVote.objects.filter(item=item, user=user).delete()
    return on, RoadmapVote.objects.filter(item=item).count()


def vote_count(item: RoadmapItem) -> int:
    return RoadmapVote.objects.filter(item=item).count()


def comments_for(item: RoadmapItem) -> QuerySet[RoadmapComment]:
    """Ko'rinadigan izohlar — yashirilganlari chiqmaydi."""
    return item.comments.filter(is_hidden=False).select_related("author")


def add_comment(user: User, item: RoadmapItem, body: str) -> RoadmapComment:
    return RoadmapComment.objects.create(item=item, author=user, body=body)


def hide_comment(comment: RoadmapComment, hidden: bool) -> RoadmapComment:
    """Post-moderatsiya: izoh o'chirilmaydi, yashiriladi."""
    comment.is_hidden = hidden
    comment.save(update_fields=["is_hidden", "updated_at"])
    return comment


__all__ = [
    "add_comment",
    "board",
    "comments_for",
    "hide_comment",
    "set_vote",
    "visible",
    "vote_count",
    "with_counts",
]
