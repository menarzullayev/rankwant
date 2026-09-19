"""Scope tekshiruvi — ADR-0008 minimal ruxsat prinsipi.

Rollar (ADR-0025): staff ICHIDA huquqlar Django `Group` lar bilan bo'linadi —
`staff-support` (foydalanuvchini ko'rish + xabar), `staff-content` (katalog +
blog), `staff-ops` (to'liq operatsion: Qvant, bloklash, testlar, analytics).
Superuser har guruhning imkoniyatiga ega. Bare `is_staff` (guruhsiz) — faqat
staff API O'QISH. Tashqi rollar (organizator, muallif) obyektga oid M2M —
`Contest.organizers`, `Problem.authors`.
"""

from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from core.models import ApiToken

STAFF_GROUP_SUPPORT = "staff-support"
STAFF_GROUP_CONTENT = "staff-content"
STAFF_GROUP_OPS = "staff-ops"
STAFF_GROUPS: tuple[str, ...] = (STAFF_GROUP_SUPPORT, STAFF_GROUP_CONTENT, STAFF_GROUP_OPS)


def has_staff_group(user: Any, *names: str) -> bool:
    """Superuser hammasiga ega; qolganlarida guruh a'zoligi tekshiriladi.

    `is_staff` shart — Group faqat staff ICHIDAGI bo'linish, ya'ni guruh
    berilgan oddiy foydalanuvchi staff yuzasiga kira olmaydi.
    """
    if not user or not getattr(user, "is_authenticated", False) or not user.is_staff:
        return False
    if user.is_superuser:
        return True
    return bool(user.groups.filter(name__in=names).exists())


def require_staff_group(user: Any, *names: str) -> None:
    """Guruh bo'lmasa 403 — xato matni kerakli guruhni atayin aytadi."""
    if has_staff_group(user, *names):
        return
    raise PermissionDenied(
        f"You do not have permission — required group: {' or '.join(names)}"
    )


class HasScope(permissions.BasePermission):
    """Session bilan kelgan so'rovda scope cheklovi yo'q.

    PAT bilan kelganda esa token kerakli scope'ga ega bo'lishi shart:
    `read` token'li so'rov submit qila olmaydi.
    """

    required_scope = ""
    message = "This token is not allowed to do that"

    def has_permission(self, request: Any, view: Any) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        auth = getattr(request, "auth", None)
        if not isinstance(auth, ApiToken):
            return True  # session — scope cheklovi yo'q
        scope = getattr(view, "required_scope", self.required_scope)
        return not scope or auth.has_scope(scope)


class CanSubmit(HasScope):
    required_scope = ApiToken.Scope.SUBMIT


class CanManageContest(HasScope):
    required_scope = ApiToken.Scope.CONTEST_MANAGE


class _StaffGroupPermission(permissions.BasePermission):
    """`is_staff` + sessiya + guruh — staff yuzalarining yangi bo'linishi.

    `IsAdminUser` va `SessionOnly` semantikasi SHU SINFDA saqlanadi: guruh
    faqat staff a'zosi uchun ma'noli, PAT bilan esa staff yuzasi umuman
    ishlamaydi (ADR-0008 — token sizishi xavfiga qarshi).
    """

    required_groups: ClassVar[tuple[str, ...]] = ()

    def has_permission(self, request: Any, view: Any) -> bool:
        if not has_staff_group(request.user, *self.required_groups):
            return False
        return not isinstance(getattr(request, "auth", None), ApiToken)


class StaffOps(_StaffGroupPermission):
    """To'liq operatsion: Qvant ±, bloklash, masala testlari, analytics."""

    required_groups = (STAFF_GROUP_OPS,)


class StaffContent(_StaffGroupPermission):
    """Kontent: maktab katalogi (ADR-0017), blog, content Article/Roadmap."""

    required_groups = (STAFF_GROUP_CONTENT,)
