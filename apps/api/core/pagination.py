"""Sahifalash — 08-technical-spec 🔒.

Katta va o'sib boruvchi ro'yxatlar (attempts, rating-history) uchun cursor,
qolganlari uchun limit/offset.
"""

from rest_framework.pagination import CursorPagination, PageNumberPagination


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
