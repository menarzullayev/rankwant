"""Admin UI uchun staff API bazasi.

Har app o'z modelini `StaffViewSet` dan meros olib `staff/<nom>/` ostida
ro'yxatga oladi. Ruxsat: FAQAT `is_staff`. Ommaviy o'qish API'lari
o'zgarmaydi — bu alohida, yozadigan yuza.
"""

from __future__ import annotations

from typing import ClassVar

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser

from core.pagination import StandardPagination


class StaffViewSet(viewsets.ModelViewSet):  # type: ignore[type-arg]
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list[str]] = []
    ordering_fields: ClassVar[list[str]] = ["pk"]
    ordering: ClassVar[list[str]] = ["-pk"]
