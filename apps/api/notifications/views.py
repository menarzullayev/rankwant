from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from core.pagination import TimeCursorPagination
from notifications.models import Notification
from notifications.serializers import MarkReadSerializer, NotificationSerializer
from notifications.services import mark_read, unread_count


@crud_summaries(
    one="bildirishnoma",
    many="bildirishnomalar",
    only=("list",),
    extra={"unread_count": "O'qilmaganlar soni", "mark_read": "Hammasini o'qilgan deb belgilash"},
)
class NotificationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet[Notification]):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TimeCursorPagination

    def get_queryset(self):  # type: ignore[no-untyped-def]
        assert isinstance(self.request.user, User)
        qs = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get("unread") == "true":
            qs = qs.filter(read_at__isnull=True)
        return qs

    @extend_schema(responses={200: None})
    @action(detail=False, methods=["get"])
    def unread_count(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        return Response({"count": unread_count(request.user)})

    @extend_schema(request=MarkReadSerializer, responses={200: None})
    @action(detail=False, methods=["post"], url_path="mark-read")
    def mark_read(self, request: Request) -> Response:
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        updated = mark_read(request.user, serializer.validated_data.get("ids"))
        return Response({"updated": updated})
