from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
from django.utils import timezone
from rest_framework import serializers

from billing import services
from billing.models import MONTHS, Order, Plan, PlanCode, PlanPrice, Subscription
from courses import teaching


class PlanPriceSerializer(serializers.ModelSerializer[PlanPrice]):
    class Meta:
        model = PlanPrice
        fields = ["months", "amount_uzs", "list_amount_uzs"]
        read_only_fields = fields


class PlanOfferSerializer(serializers.ModelSerializer[Plan]):
    features = serializers.SerializerMethodField()
    prices = PlanPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ["code", "is_on_sale", "features", "prices"]
        read_only_fields = fields

    def get_features(self, obj: Plan) -> list[str]:
        return services.features(obj, self.context.get("locale") or "uz")


class PeriodSerializer(serializers.ModelSerializer[Subscription]):
    #: Already begun (a later one waits for the current plan to end).
    running = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ["plan", "starts_at", "ends_at", "running"]
        read_only_fields = fields

    def get_running(self, obj: Subscription) -> bool:
        return obj.starts_at <= timezone.now()


class BillingOverviewSerializer(serializers.Serializer[dict[str, Any]]):
    plans = PlanOfferSerializer(many=True)
    #: Payment methods whose merchant settings are present.
    providers = serializers.ListField(child=serializers.CharField())
    #: The plan in force now ("free" for guests and free accounts).
    plan = serializers.CharField()
    plan_expires_at = serializers.DateTimeField(allow_null=True)
    #: Paid periods not over yet, the running one included.
    periods = PeriodSerializer(many=True)


class OrderCourseSerializer(serializers.Serializer[dict[str, Any]]):
    slug = serializers.CharField()
    title = serializers.CharField()


class OrderSerializer(serializers.ModelSerializer[Order]):
    course = serializers.SerializerMethodField()
    pay_url = serializers.SerializerMethodField()
    period = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "kind",
            "plan",
            "months",
            "course",
            "amount_uzs",
            "provider",
            "status",
            "created_at",
            "paid_at",
            "period",
            "pay_url",
        ]
        read_only_fields = fields

    @extend_schema_field(OrderCourseSerializer(allow_null=True))
    def get_course(self, obj: Order) -> dict[str, Any] | None:
        if obj.course is None:
            return None
        brief = teaching.brief(obj.course, self.context.get("locale") or "")
        return {"slug": brief["slug"], "title": brief["title"]}

    def get_pay_url(self, obj: Order) -> str | None:
        """The provider's page, while the order still waits for payment."""
        if obj.status != Order.Status.PENDING:
            return None
        return services.pay_url(obj, self.context.get("ui_locale") or "uz")

    @extend_schema_field(PeriodSerializer(allow_null=True))
    def get_period(self, obj: Order) -> dict[str, Any] | None:
        sub = getattr(obj, "subscription", None)
        return PeriodSerializer(sub).data if sub is not None else None


class OrderCreateSerializer(serializers.Serializer[dict[str, Any]]):
    kind = serializers.ChoiceField(choices=Order.Kind.choices)
    plan = serializers.ChoiceField(choices=PlanCode.choices, required=False)
    months = serializers.ChoiceField(choices=[(m, str(m)) for m in MONTHS], required=False)
    #: A paid course's slug, for `kind=course`.
    course = serializers.SlugField(required=False)
    provider = serializers.ChoiceField(choices=Order.Provider.choices)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["kind"] == Order.Kind.PLAN and not (attrs.get("plan") and attrs.get("months")):
            raise serializers.ValidationError("A plan order needs a plan and a period.")
        if attrs["kind"] == Order.Kind.COURSE and not attrs.get("course"):
            raise serializers.ValidationError("A course order needs a course.")
        return attrs
