from __future__ import annotations

from django.http import QueryDict
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User
from core.openapi_docs import crud_summaries
from core.pagination import TimeCursorPagination
from notifications import email as email_channel
from notifications import services
from notifications.models import Notification
from notifications.serializers import (
    EmailUnsubscribeResultSerializer,
    EmailUnsubscribeSerializer,
    MarkReadSerializer,
    NotificationIdsSerializer,
    NotificationSerializer,
    NotificationSummarySerializer,
    NotificationUpdatedSerializer,
)


@crud_summaries(
    one="bildirishnoma",
    many="bildirishnomalar",
    only=("list", "destroy"),
    extra={
        "unread_count": "O'qilmaganlar soni",
        "summary": "Qo'ng'iroq va tablar uchun sonlar",
        "mark_read": "O'qilgan deb belgilash",
        "mark_unread": "O'qilmagan qilish",
        "mark_seen": "Qo'ng'iroq ochildi — hammasi ko'rilgan",
        "clear_read": "O'qilganlarni o'chirish",
    },
)
class NotificationViewSet(
    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet[Notification]
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TimeCursorPagination

    def get_queryset(self):  # type: ignore[no-untyped-def]
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        assert isinstance(self.request.user, User)
        qs = Notification.objects.filter(user=self.request.user)
        if self.action != "list":
            return qs
        if self.request.query_params.get("unread") == "true":
            qs = qs.filter(read_at__isnull=True)
        # `?kind=duel,hack` — values outside the enum are dropped, so a
        # typo lists nothing rather than everything.
        wanted = self.request.query_params.get("kind")
        if wanted:
            qs = qs.filter(kind__in=set(wanted.split(",")) & set(Notification.Kind.values))
        return qs

    @extend_schema(responses={200: None})
    @action(detail=False, methods=["get"])
    def unread_count(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        return Response({"count": services.unread_count(request.user)})

    @extend_schema(responses={200: NotificationSummarySerializer})
    @action(detail=False, methods=["get"], pagination_class=None)
    def summary(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        return Response(services.summary(request.user))

    @extend_schema(request=MarkReadSerializer, responses={200: NotificationUpdatedSerializer})
    @action(detail=False, methods=["post"], url_path="mark-read")
    def mark_read(self, request: Request) -> Response:
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        updated = services.mark_read(request.user, serializer.validated_data.get("ids"))
        return Response({"updated": updated})

    @extend_schema(
        request=NotificationIdsSerializer, responses={200: NotificationUpdatedSerializer}
    )
    @action(detail=False, methods=["post"], url_path="mark-unread")
    def mark_unread(self, request: Request) -> Response:
        serializer = NotificationIdsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        updated = services.mark_unread(request.user, serializer.validated_data["ids"])
        return Response({"updated": updated})

    @extend_schema(request=None, responses={200: NotificationUpdatedSerializer})
    @action(detail=False, methods=["post"], url_path="mark-seen")
    def mark_seen(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        return Response({"updated": services.mark_seen(request.user)})

    @extend_schema(request=None, responses={200: NotificationUpdatedSerializer})
    @action(detail=False, methods=["post"], url_path="clear-read")
    def clear_read(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        return Response({"updated": services.clear_read(request.user)})


class EmailUnsubscribeView(APIView):
    """One-click unsubscribe from notification email (`notifications.email`).

    No session and no CSRF: a mail client posts here on its own (RFC 8058,
    body `List-Unsubscribe=One-Click`, the token in the URL), and a reader
    opens the link from another device. The signed token is the whole
    credential and it can do one thing only — switch email off.

    GET only reads the token (the confirmation page asks first): link
    scanners in mail systems open every URL, and a GET that unsubscribed
    would switch people's email off behind their backs.
    """

    authentication_classes = ()
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser]

    def _target(self, request: Request) -> tuple[User, str] | None:
        token = request.query_params.get("token") or ""
        if not token and isinstance(request.data, dict | QueryDict):
            token = str(request.data.get("token") or "")
        found = email_channel.read_token(token) if token else None
        if found is None:
            return None
        user = User.objects.filter(pk=found[0]).first()
        return (user, found[1]) if user is not None else None

    @extend_schema(
        summary="Obunani tekshirish (email)",
        parameters=[OpenApiParameter("token", str, required=True)],
        responses={200: EmailUnsubscribeResultSerializer},
    )
    def get(self, request: Request) -> Response:
        target = self._target(request)
        if target is None:
            return Response({"detail": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"kind": target[1], "done": False})

    @extend_schema(
        summary="Email bildirishnomasini o'chirish",
        request=EmailUnsubscribeSerializer,
        responses={200: EmailUnsubscribeResultSerializer},
    )
    def post(self, request: Request) -> Response:
        target = self._target(request)
        if target is None:
            return Response({"detail": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)
        user, kind = target
        email_channel.unsubscribe(user, kind)
        return Response({"kind": kind, "done": True})
