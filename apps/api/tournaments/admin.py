from django.contrib import admin

from tournaments.models import Tournament, TournamentStage, TournamentStanding


class StageInline(admin.TabularInline):
    model = TournamentStage
    extra = 1
    autocomplete_fields = ("contest",)


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "start_at", "end_at", "is_public")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [StageInline]


@admin.register(TournamentStanding)
class TournamentStandingAdmin(admin.ModelAdmin):
    list_display = ("tournament", "rank", "user", "points", "solved_total")
    list_select_related = ("tournament", "user")
