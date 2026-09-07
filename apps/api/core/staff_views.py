"""Staff (admin UI) — foydalanuvchilar boshqaruvi.

Yaratish va o'chirish YO'Q: foydalanuvchi ro'yxatdan o'tadi, admin uni
bloklaydi (`is_active`) — o'chirmaydi (ledger va reyting tarixi saqlanadi).
"""

from __future__ import annotations

from typing import Any

from django.db.models import F, QuerySet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.staff import StaffViewSet
from core.staff_serializers import (
    QvantAdjustSerializer,
    StaffNotifySerializer,
    StaffUserSerializer,
)
from notifications import services as notifications
from notifications.models import Notification
from qvant import ledger
from qvant.models import QvantTransaction


class StaffUserViewSet(StaffViewSet):
    serializer_class = StaffUserSerializer
    lookup_field = "username"
    #: Standart router shabloni nuqtani kesadi — `a.b` username 404 berardi.
    lookup_value_regex = "[^/]+"
    search_fields = ["username", "display_name", "email"]
    ordering_fields = ["date_joined", "rating_skills"]
    ordering = ["-date_joined"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.annotate(qvant_balance=F("wallet__balance"))

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        raise MethodNotAllowed("POST")

    @action(detail=True, methods=["post"])
    def qvant(self, request: Request, username: str | None = None) -> Response:
        """Qvant tuzatish: musbat — kunlik shiftsiz kredit, manfiy — debit."""
        user = self.get_object()
        ser = QvantAdjustSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        amount: int = ser.validated_data["amount"]
        note: str = ser.validated_data["note"]
        ref = {"ref_type": "admin", "ref_id": note[:64]}
        try:
            if amount > 0:
                tx = ledger.credit(
                    user, amount, QvantTransaction.Reason.ADMIN, respect_cap=False, **ref
                )
            else:
                tx = ledger.debit(user, -amount, QvantTransaction.Reason.ADMIN, **ref)
        except ledger.InsufficientBalance as exc:
            raise ValidationError({"amount": f"Balans yetarli emas: {exc}"}) from exc
        assert tx is not None  # respect_cap=False — kredit har doim yoziladi
        return Response({"amount": tx.amount, "balance": tx.balance_after})

    @action(detail=True, methods=["post"])
    def notify(self, request: Request, username: str | None = None) -> Response:
        user = self.get_object()
        ser = StaffNotifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        n = notifications.notify(
            user,
            Notification.Kind.SYSTEM,
            ser.validated_data["title"],
            body=ser.validated_data["body"],
            ref_type="admin",
        )
        return Response({"id": n.pk if n else None}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def broadcast(self, request: Request) -> Response:
        ser = StaffNotifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        count = notifications.notify_many(
            User.objects.filter(is_active=True).iterator(),
            Notification.Kind.SYSTEM,
            ser.validated_data["title"],
            body=ser.validated_data["body"],
            ref_type="admin",
        )
        return Response({"count": count}, status=status.HTTP_201_CREATED)
