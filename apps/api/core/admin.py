from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpRequest, HttpResponse

from core import mail_quota
from core.models import ApiToken, EmailDelivery, School, SiteAppearance, User


@admin.register(User)
class RankWantUserAdmin(UserAdmin):  # type: ignore[type-arg]
    list_display = ("username", "email", "rating_skills", "rating_contest", "is_staff")
    list_filter = ("is_staff", "is_active", "locale")
    search_fields = ("username", "email", "display_name")
    fieldsets = (
        *(UserAdmin.fieldsets or ()),
        (
            "RankWant",
            {
                "fields": (
                    "display_name",
                    "avatar_url",
                    "bio",
                    "telegram_id",
                    "locale",
                    "theme",
                    "rating_skills",
                    "rating_contest",
                    "rating_activity",
                    "rating_challenges",
                    "rated_contest_count",
                    "streak_count",
                    "streak_freeze_until",
                    "last_active_date",
                )
            },
        ),
        (
            # ADR-0024. The counters mirror their source tables; edit those, or
            # run `manage.py recount_user_stats`, instead of the counters.
            "Competitor parity",
            {
                "fields": (
                    "solved_count",
                    "streak_max",
                    "max_rating_skills",
                    "max_rating_contest",
                    "max_rating_activity",
                    "max_rating_challenges",
                    "last_seen_at",
                    "shirt_size",
                )
            },
        ),
        (
            "Dormant until their features exist",
            {
                "classes": ("collapse",),
                "fields": (
                    "plan",
                    "plan_expires_at",
                    "postal_recipient",
                    "postal_country",
                    "postal_region",
                    "postal_city",
                    "postal_address",
                    "postal_code",
                    "coach_can_view_attempts",
                    "message_min_rating",
                    "contribution",
                    "device_fingerprint",
                    "duel_ready_until",
                ),
            },
        ),
    )
    readonly_fields = (
        "solved_count",
        "streak_max",
        "max_rating_skills",
        "max_rating_contest",
        "max_rating_activity",
        "max_rating_challenges",
        "last_seen_at",
    )


@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "prefix", "expires_at", "revoked_at", "last_used_at")
    list_filter = ("revoked_at",)
    search_fields = ("name", "user__username", "prefix")
    readonly_fields = ("token_hash", "prefix", "created_at", "last_used_at")


@admin.register(EmailDelivery)
class EmailDeliveryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Diagnostika jurnali + kunlik kvota paneli.

    Ro'yxat faqat O'QISH uchun: yozuvlar kod tomonidan yaratiladi, admin
    orqali qo'shilsa haqiqiy yuborish tarixi buzilardi.

    `changelist_view` ustiga kvota bloki qo'shiladi — chunki «bugun
    qancha qoldi» savoli eng ko'p so'raladi va u shu sahifaning o'zida
    turishi kerak (`core.mail_quota`).
    """

    list_display = ("created_at", "to_email", "purpose", "provider", "status")
    list_filter = ("status", "purpose", "provider")
    search_fields = ("to_email", "subject")
    readonly_fields = (
        "to_email",
        "purpose",
        "subject",
        "provider",
        "status",
        "attempts",
        "created_at",
    )
    date_hierarchy = "created_at"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        context = dict(extra_context or {})
        context["quota"] = mail_quota.usage()
        context["quota_total"] = mail_quota.total_remaining()
        context["quota_with_queue"] = mail_quota.total_remaining_with_queue()
        context["quota_failures"] = mail_quota.failures()
        return super().changelist_view(request, extra_context=context)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Maktab katalogi — moderator shu yerdan to'ldiradi (ADR-0017)."""

    list_display = ("name", "kind", "region", "district", "is_active")
    list_filter = ("kind", "region", "is_active")
    search_fields = ("name",)


@admin.register(SiteAppearance)
class SiteAppearanceAdmin(admin.ModelAdmin):
    """Default appearance — bitta qator (D37).

    `appearance` — `ui_prefs.appearance` bilan AYNI shakl:
    `{"style": "clay", "accent": {"hue": 215, "sat": 75}, "font": null,
      "size": 100, "density": "comfortable"}`

    Bo'sh qoldirilsa standart kod qiymati ishlatiladi (D26: `clay`).
    """

    list_display = ("__str__", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request: Any) -> bool:
        # Singleton: ikkinchi qator qo'shish mantiqsiz va qaysi biri
        # qo'llanishi noaniq bo'lardi.
        return not SiteAppearance.objects.exists()

    def has_delete_permission(self, request: Any, obj: Any = None) -> bool:
        return False
