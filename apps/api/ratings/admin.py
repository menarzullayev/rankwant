from django.contrib import admin

from ratings.models import RatingHistory, UserSolvedProblem


@admin.register(UserSolvedProblem)
class UserSolvedProblemAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "difficulty_at_solve", "first_ac_at")
    search_fields = ("user__username", "problem__slug")


@admin.register(RatingHistory)
class RatingHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "rating_type",
        "value_before",
        "value_after",
        "delta",
        "reason",
        "created_at",
    )
    list_filter = ("rating_type", "reason")
    search_fields = ("user__username", "ref_id")
    readonly_fields = tuple(f.name for f in RatingHistory._meta.fields)
