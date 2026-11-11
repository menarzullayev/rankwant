from django.contrib import admin

from coaching.models import CoachLink, Recommendation


@admin.register(CoachLink)
class CoachLinkAdmin(admin.ModelAdmin):
    list_display = ("coach", "student", "status", "can_view_attempts", "created_at")
    list_filter = ("status",)
    search_fields = ("coach__username", "student__username")
    raw_id_fields = ("coach", "student")


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("link", "problem", "created_at")
    raw_id_fields = ("link", "problem")
