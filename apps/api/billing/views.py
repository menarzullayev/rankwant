from __future__ import annotations

import json
from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing import click, payme, services
from billing.models import Order, Plan
from billing.serializers import (
    BillingOverviewSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)
from core.models import User
from courses.views import content_locale, published


def _ui_locale(request: Request) -> str:
    return str(getattr(request, "LANGUAGE_CODE", "") or "uz").split("-")[0]


class BillingOverviewView(APIView):
    """Plans on sale with their prices, and the reader's own plan."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: BillingOverviewSerializer})
    def get(self, request: Request) -> Response:
        plans = Plan.objects.prefetch_related("prices").order_by("id")
        user = request.user
        periods: list[Any] = []
        plan, expires = "free", None
        if isinstance(user, User):
            services.sync_user_plan(user)
            plan, expires = user.plan, user.plan_expires_at
            periods = list(
                user.subscriptions.filter(revoked_at__isnull=True, ends_at__gt=timezone.now())
            )
        data = {
            "plans": plans,
            "providers": services.providers(),
            "plan": plan,
            "plan_expires_at": expires,
            "periods": periods,
        }
        context = {"locale": content_locale(request) or "uz"}
        return Response(BillingOverviewSerializer(data, context=context).data)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet[Order],
):
    """The reader's own orders; paying happens on the provider's page."""

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet[Order]:
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        assert isinstance(self.request.user, User)
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("course", "subscription")
            .prefetch_related("course__translations")
        )

    def get_serializer_context(self) -> dict[str, Any]:
        return {
            **super().get_serializer_context(),
            "locale": content_locale(self.request),
            "ui_locale": _ui_locale(self.request),
        }

    @extend_schema(request=OrderCreateSerializer, responses={201: OrderSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        data = OrderCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        assert isinstance(request.user, User)
        if values["kind"] == Order.Kind.PLAN:
            order = services.create_plan_order(
                request.user, values["plan"], int(values["months"]), values["provider"]
            )
        else:
            course = get_object_or_404(published(), slug=values["course"])
            order = services.create_course_order(request.user, course, values["provider"])
        return Response(
            OrderSerializer(order, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=None, responses={200: OrderSerializer})
    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, pk: str | None = None) -> Response:
        order = self.get_object()
        services.abandon(order)
        order.refresh_from_db()
        return Response(OrderSerializer(order, context=self.get_serializer_context()).data)


@method_decorator(csrf_exempt, name="dispatch")
class PaymeWebhookView(APIView):
    """Payme Merchant API endpoint (JSON-RPC 2.0, Basic auth with the key).

    Answers HTTP 200 for every call, errors included: Payme reads any other
    status as a system error.
    """

    authentication_classes: list[Any] = []
    permission_classes = [AllowAny]
    throttle_classes: list[Any] = []

    @extend_schema(exclude=True)
    def post(self, request: Request) -> Response:
        try:
            body = json.loads(request.body or b"null")
        except (ValueError, UnicodeDecodeError):
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": payme.BAD_REQUEST, "data": None},
                }
            )
        return Response(payme.handle(body, request.headers.get("Authorization", "")))


@method_decorator(csrf_exempt, name="dispatch")
class ClickWebhookView(APIView):
    """Click SHOP-API endpoint: one URL for Prepare and Complete."""

    authentication_classes: list[Any] = []
    permission_classes = [AllowAny]
    throttle_classes: list[Any] = []
    parser_classes = [FormParser, MultiPartParser]

    @extend_schema(exclude=True)
    def post(self, request: Request) -> Response:
        form: Any = request.data
        data = {key: str(form.get(key, "")) for key in form}
        return Response(click.handle(data))
