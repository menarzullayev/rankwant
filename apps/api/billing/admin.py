from __future__ import annotations

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from billing import services
from billing.models import ClickTransaction, Order, PaymeTransaction, Plan, PlanPrice, Subscription


class PlanPriceInline(admin.TabularInline):
    model = PlanPrice
    extra = 0


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Prices and the features text are set here (owner decision 2026-11-10)."""

    list_display = ["code", "is_on_sale"]
    inlines = [PlanPriceInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "kind",
        "plan",
        "months",
        "course",
        "amount_uzs",
        "provider",
        "status",
        "created_at",
    ]
    list_filter = ["status", "provider", "kind"]
    search_fields = ["id", "user__username"]
    readonly_fields = [f.name for f in Order._meta.fields]
    actions = ["revoke_refunded"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @admin.action(description="Refunded outside the site: revoke access")
    def revoke_refunded(self, request: HttpRequest, queryset: QuerySet[Order]) -> None:
        # A Click refund is made in Click's merchant cabinet and sends no
        # callback; staff record it here so access ends too.
        for order in queryset.filter(status=Order.Status.PAID):
            services.revoke(order)
        self.message_user(request, "Revoked.", messages.SUCCESS)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "starts_at", "ends_at", "revoked_at"]
    list_filter = ["plan"]
    search_fields = ["user__username"]
    readonly_fields = [f.name for f in Subscription._meta.fields]


@admin.register(PaymeTransaction)
class PaymeTransactionAdmin(admin.ModelAdmin):
    list_display = ["payme_id", "order", "amount", "state", "reason"]
    readonly_fields = [f.name for f in PaymeTransaction._meta.fields]


@admin.register(ClickTransaction)
class ClickTransactionAdmin(admin.ModelAdmin):
    list_display = ["click_trans_id", "order", "amount", "status", "created_at"]
    readonly_fields = [f.name for f in ClickTransaction._meta.fields]
