"""Scope tekshiruvi — ADR-0008 minimal ruxsat prinsipi."""

from __future__ import annotations

from typing import Any

from rest_framework import permissions

from core.models import ApiToken


class HasScope(permissions.BasePermission):
    """Session bilan kelgan so'rovda scope cheklovi yo'q.

    PAT bilan kelganda esa token kerakli scope'ga ega bo'lishi shart:
    `read` token'li so'rov submit qila olmaydi.
    """

    required_scope = ""
    message = "Token bu amal uchun ruxsatga ega emas"

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
