from django.contrib import admin

from judging.models import Attempt, AttemptTestResult


class TestResultInline(admin.TabularInline):
    model = AttemptTestResult
    extra = 0
    readonly_fields = ("index", "verdict", "time_ms", "memory_kb")
    can_delete = False


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "problem",
        "language",
        "verdict",
        "time_ms",
        "memory_kb",
        "created_at",
    )
    list_filter = ("verdict", "language")
    search_fields = ("user__username", "problem__slug")
    readonly_fields = ("created_at", "judged_at", "source_size")
    inlines = [TestResultInline]
