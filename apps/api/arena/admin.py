from django.contrib import admin

from arena.models import ArenaParticipation, ArenaQuestion, ArenaRound


class ArenaQuestionInline(admin.TabularInline):
    model = ArenaQuestion
    extra = 1
    autocomplete_fields = ("question",)


@admin.register(ArenaRound)
class ArenaRoundAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "start_at", "seconds_per_question", "is_public")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ArenaQuestionInline]


@admin.register(ArenaParticipation)
class ArenaParticipationAdmin(admin.ModelAdmin):
    list_display = ("round", "user", "score", "correct_count", "total_ms")
    list_select_related = ("round", "user")
