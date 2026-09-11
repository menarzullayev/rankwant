from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import ApiToken, School, User


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
    )


@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "prefix", "expires_at", "revoked_at", "last_used_at")
    list_filter = ("revoked_at",)
    search_fields = ("name", "user__username", "prefix")
    readonly_fields = ("token_hash", "prefix", "created_at", "last_used_at")


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Maktab katalogi — moderator shu yerdan to'ldiradi (ADR-0017)."""

    list_display = ("name", "kind", "region", "district", "is_active")
    list_filter = ("kind", "region", "is_active")
    search_fields = ("name",)
