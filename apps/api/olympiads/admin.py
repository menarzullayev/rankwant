from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from olympiads.models import Event, Participant, ProblemSet, Result, Season, Task


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "start_date", "end_date")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "season", "start_date", "status")
    list_filter = ("season", "kind")
    search_fields = ("slug", "title")


@admin.register(ProblemSet)
class ProblemSetAdmin(admin.ModelAdmin):
    list_display = ("event", "slug", "title")


@admin.action(description="Remove on request (hide; a later import keeps it hidden)")
def take_down(modeladmin: Any, request: HttpRequest, queryset: QuerySet[Any]) -> None:
    queryset.update(removed_at=timezone.now())


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "problem_set", "from_kep", "removed_at")
    list_filter = ("from_kep",)
    search_fields = ("slug", "title")
    actions = (take_down,)


@admin.action(
    description="Remove on request (hide, clear the name; a later import keeps it hidden)"
)
def remove_person(modeladmin: Any, request: HttpRequest, queryset: QuerySet[Participant]) -> None:
    queryset.update(removed_at=timezone.now(), full_name="")


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("slug", "full_name", "country_code", "removed_at")
    search_fields = ("slug", "full_name")
    actions = (remove_person,)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("event", "participant", "rank", "score", "medal")
    list_filter = ("event",)
