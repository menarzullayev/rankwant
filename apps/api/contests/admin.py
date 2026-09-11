from django.contrib import admin

from contests.models import Certificate, Contest, ContestProblem, ContestRegistration, Standing


class ContestProblemInline(admin.TabularInline):
    model = ContestProblem
    extra = 1


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title",
        "start_at",
        "end_at",
        "scoring_type",
        "is_rated",
        "ratings_applied_at",
    )
    list_filter = ("is_rated", "is_virtual", "is_public", "scoring_type")
    search_fields = ("slug", "title")
    # O'n ming foydalanuvchini ro'yxatga yuklamaslik uchun — qidiruv bilan.
    autocomplete_fields = ("jury",)
    inlines = [ContestProblemInline]
    readonly_fields = ("ratings_applied_at", "created_at")


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ("contest", "rank", "user", "solved_count", "penalty")
    list_filter = ("contest",)


admin.site.register(ContestRegistration)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("id", "contest", "user", "place", "tier", "issued_at")
    list_filter = ("tier",)
    search_fields = ("user__username", "contest__slug")
    readonly_fields = ("id", "issued_at")
