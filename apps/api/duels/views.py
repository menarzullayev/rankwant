from __future__ import annotations

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from duels.models import Duel
from duels.serializers import DuelCreateSerializer, DuelRecordSerializer, DuelSerializer
from duels.services import DuelError, accept, cancel, create, record


def _error(exc: DuelError) -> Response:
    return Response(
        {"error": {"code": exc.code, "message": exc.message, "details": {}}},
        status=status.HTTP_400_BAD_REQUEST,
    )


@crud_summaries(one="duel", many="duellar", only=("list", "retrieve"))
class DuelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet[Duel],
):
    """1v1 — PRD Phase 3.

    `list` — kutish xonasi: hozir ochiq chaqiriqlar. O'z duellari `mine` da.
    """

    serializer_class = DuelSerializer
    lookup_field = "slug"

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        qs = Duel.objects.select_related("challenger", "opponent", "winner")
        if self.action == "list":
            return qs.filter(status=Duel.Status.OPEN).order_by("start_at")
        return qs

    @extend_schema(request=DuelCreateSerializer, responses={201: DuelSerializer})
    def create(self, request: Request, *args: object, **kwargs: object) -> Response:
        serializer = DuelCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            duel = create(request.user, **serializer.validated_data)
        except DuelError as exc:
            return _error(exc)
        return Response(
            DuelSerializer(duel, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=None, responses={200: DuelSerializer})
    @action(detail=True, methods=["post"])
    def accept(self, request: Request, slug: str | None = None) -> Response:
        assert isinstance(request.user, User)
        try:
            duel = accept(request.user, self.get_object())
        except DuelError as exc:
            return _error(exc)
        return Response(DuelSerializer(duel, context={"request": request}).data)

    @extend_schema(request=None, responses={200: DuelSerializer})
    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, slug: str | None = None) -> Response:
        assert isinstance(request.user, User)
        try:
            duel = cancel(request.user, self.get_object())
        except DuelError as exc:
            return _error(exc)
        return Response(DuelSerializer(duel, context={"request": request}).data)

    @extend_schema(responses={200: DuelSerializer(many=True)})
    @action(detail=False, methods=["get"])
    def mine(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        qs = (
            Duel.objects.filter(Q(challenger=request.user) | Q(opponent=request.user))
            .select_related("challenger", "opponent", "winner")
            .order_by("-created_at")[:50]
        )
        return Response(
            {
                "record": record(request.user),
                "results": DuelSerializer(qs, many=True, context={"request": request}).data,
            }
        )

    @extend_schema(responses={200: DuelRecordSerializer})
    @action(detail=False, methods=["get"], url_path=r"record/(?P<username>[^/.]+)")
    def user_record(self, request: Request, username: str | None = None) -> Response:
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(record(user))
