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
    ordering = "-created_at"
