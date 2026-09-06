"""Yagona xato formati — 08-technical-spec 🔒.

{"error": {"code": "...", "message": "...", "details": {}}}
"""

from __future__ import annotations

from typing import Any

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = drf_handler(exc, context)
    if response is None:
        return None

    code = "error"
    if isinstance(exc, exceptions.APIException):
        code = getattr(exc, "default_code", "error") or "error"

    detail = response.data
    message = ""
    details: dict[str, Any] = {}
    if isinstance(detail, dict):
        raw = detail.get("detail")
        if raw is not None:
            message = str(raw)
        else:
            details = detail
            message = "Kiritilgan ma'lumot noto'g'ri"
    elif isinstance(detail, list):
        details = {"errors": detail}
        message = "Kiritilgan ma'lumot noto'g'ri"
    else:
        message = str(detail)

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response
