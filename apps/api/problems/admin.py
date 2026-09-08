"""Django admin — PRD P0-2 ning asosiy vositasi (ADR-0003 sababi)."""

from django.contrib import admin

from problems.models import Language, Problem, Subtask, TestCase, Topic


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ("order", "input_ref", "output_ref", "is_sample", "points", "subtask")


class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 0


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "slug",
        "title",
        "difficulty",
        "level_label",
        "is_public",
        "solved_count",
        "attempt_count",
    )
    list_filter = ("is_public", "checker_type", "topics")
    search_fields = ("slug", "title", "code")
    filter_horizontal = ("topics",)
    readonly_fields = ("code", "solved_count", "attempt_count", "created_at", "updated_at")
    inlines = [SubtaskInline, TestCaseInline]
    fieldsets = (
        (None, {"fields": ("slug", "title", "is_public", "author")}),
        ("Matn", {"fields": ("statement", "statement_locale")}),
        ("Baholash", {"fields": ("difficulty", "topics")}),
        (
            "Judge",
            {
                "fields": (
                    "time_limit_ms",
                    "memory_limit_kb",
                    "checker_type",
                    "interactor_language",
                    "interactor_source",
                )
            },
        ),
        ("Manba", {"fields": ("source", "source_url")}),
        ("Statistika", {"fields": ("solved_count", "attempt_count", "created_at", "updated_at")}),
    )

    @admin.display(description="Daraja")
    def level_label(self, obj: Problem) -> str:
        return obj.level_label


admin.site.register(Topic)
admin.site.register(Language)
