"""Sahifalash — 08-technical-spec 🔒.

Katta va o'sib boruvchi ro'yxatlar (attempts, rating-history) uchun cursor,
qolganlari uchun limit/offset.
"""

from typing import Any, ClassVar

from django.db.models import QuerySet
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.request import Request


class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class TimeCursorPagination(CursorPagination):
    page_size = 25
    max_page_size = 100
    page_size_query_param = "page_size"
    #: `-pk` — TIEBREAKER, bezak emas. Yolg'iz `-created_at` noyob emas:
    #: teng vaqtli qatorlarning tartibi so'rovdan so'rovga o'zgarishi
    #: mumkin va kursor boshqa qatorga tushadi. O'lchandi — bir xil
    #: vaqtli 70 qatordan 69 tasi qaytgan, bittasi ikki marta, bittasi
    #: umuman tushib qolgan. Contest spike'ida bir necha yuborish bir
    #: mikrosoniyaga tushishi mumkin.
    ordering = ("-created_at", "-pk")


class SortableCursorPagination(TimeCursorPagination):
    """`TimeCursorPagination` + foydalanuvchi tanlaydigan saralash.

    Nega ALOHIDA sinf, `TimeCursorPagination` ning o'zi emas: uni oltita
    viewset ishlatadi (`core`, `hacks`, `judging`, `notifications`,
    `qvant`) va ularning API shartnomasi o'zgarmasligi kerak. Yangi
    `ordering` parametri faqat shu sinfni tanlagan viewset'da paydo
    bo'ladi.

    ⚠️ Saralash maydoni KURSOR O'QI bo'lib qoladi — DRF pozitsiyani
    `ordering[0]` dan oladi. Shu sababli maydon ikki shartni bajarishi
    kerak:

      * **NULL bo'lmasligi** — aks holda kursor taqqoslanmaydi;
      * **o'zgarmas bo'lishi** — rejudge qiymatni o'zgartirsa, eski
        kursor boshqa qatorga tushadi (DRF hujjati ham shuni aytadi).

    `time_ms`, `memory_kb`, `source_size` — uchalasi ham
    `PositiveIntegerField(default=0)`, ya'ni NULL emas. O'zgarish esa
    faqat rejudge'da bo'ladi (`TESTING_ABORTED`), ya'ni kamdan-kam.

    Ro'yxatda yo'q qiymat JIM rad etiladi (standart tartib qaytadi):
    foydalanuvchi satri `order_by()` ga hech qachon yetib bormaydi.
    """

    #: API qiymati → model maydoni. Bo'sh lug'at = saralash yo'q.
    ordering_fields: ClassVar[dict[str, str]] = {}
    #: So'rov parametri nomi. `ordering` — DRF ning umumiy atamasi.
    ordering_query_param: ClassVar[str] = "ordering"

    def get_ordering(self, request: Request, queryset: QuerySet[Any], view: Any) -> tuple[str, ...]:
        raw = request.query_params.get(self.ordering_query_param)
        field = self.ordering_fields.get(raw) if raw else None
        if field is None:
            return self.ordering  # type: ignore[return-value]
        #: Tiebreaker asosiy yo'nalish bilan BIR XIL bo'lishi kerak:
        #: `-time_ms, pk` da teng qiymatli qatorlar teskari chiqadi va
        #: kursor sahifalari orasida tartib aralashib ketadi.
        return (field, "-pk" if field.startswith("-") else "pk")
