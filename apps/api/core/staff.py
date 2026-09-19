"""Admin UI uchun staff API bazasi.

Har app o'z modelini `StaffViewSet` dan meros olib `staff/<nom>/` ostida
ro'yxatga oladi. Ruxsat: FAQAT `is_staff`. Ommaviy o'qish API'lari
o'zgarmaydi — bu alohida, yozadigan yuza.
"""

from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import filters, permissions, viewsets
from rest_framework.permissions import IsAdminUser

from core.models import ApiToken
from core.pagination import StandardPagination


class SessionOnly(permissions.BasePermission):
    """Staff yuzasi PAT bilan ishlamaydi — faqat sessiya.

    ADR-0008: PAT ochiq API va bot uchun. Aks holda xodimning oddiy
    `read` tokeni sizib chiqsa u bilan foydalanuvchini bloklash yoki
    masala o'chirish mumkin bo'lardi — scope tekshiruvi bazaviy
    viewset'da yo'q edi va IsAdminUser buni farqlamaydi.
    """

    message = "The staff API accepts a session, not an API token"

    def has_permission(self, request: Any, view: Any) -> bool:
        return not isinstance(getattr(request, "auth", None), ApiToken)


class StaffViewSet(viewsets.ModelViewSet):  # type: ignore[type-arg]
    permission_classes = [IsAdminUser, SessionOnly]
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar[list[str]] = []
    ordering_fields: ClassVar[list[str]] = ["pk"]
    ordering: ClassVar[list[str]] = ["-pk"]
