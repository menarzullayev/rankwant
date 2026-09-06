"""Yagona xato formati — 08-technical-spec 🔒.

{"error": {"code": "...", "message": "...", "details": {}}}
"""

from __future__ import annotations

from typing import Any

import redis
from django.db.utils import OperationalError
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_handler

#: Bog'liqlik uzilishi — kod xatosi emas. 10-operations «toza 503»
#: va'da qiladi; ishlov berilmasa Django 500 va stack trace qaytaradi.
UNAVAILABLE = (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError, OperationalError)


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    if isinstance(exc, UNAVAILABLE):
        return Response(
            {
                "error": {
                    "code": "dependency_unavailable",
                    "message": "Xizmat vaqtincha mavjud emas, birozdan keyin urinib ko'ring",
                    "details": {},
                }
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

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
