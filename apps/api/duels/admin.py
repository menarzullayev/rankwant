from django.contrib import admin

from duels.models import Duel, DuelProblem


class DuelProblemInline(admin.TabularInline):
    model = DuelProblem
    extra = 0


@admin.register(Duel)
class DuelAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "challenger", "opponent", "status", "start_at", "winner")
    list_filter = ("status",)
    list_select_related = ("challenger", "opponent", "winner")
    inlines = [DuelProblemInline]
