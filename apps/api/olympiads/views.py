"""The olympiad archive over the API (ADR-0062 § 2.6). Read only, public."""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Prefetch, Q
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from content.exercise_keys import exercise_key
from olympiads.models import Event, Participant, ProblemSet, Result, Season, Task
from problems.lookup import public_problems, source_key_index

# ── shapes ───────────────────────────────────────────────────────────────


class EventCardSerializer(serializers.ModelSerializer[Event]):
    task_count = serializers.IntegerField(read_only=True, default=0)
    result_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Event
        fields = [
            "slug",
            "code",
            "title",
            "short_title",
            "summary",
            "kind",
            "status",
            "start_date",
            "end_date",
            "date_label",
            "location",
            "is_featured",
            "routes",
            "task_count",
            "result_count",
        ]


class SeasonSerializer(serializers.ModelSerializer[Season]):
    events = EventCardSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ["slug", "title", "summary", "start_date", "end_date", "routes", "events"]


class TaskRowSerializer(serializers.ModelSerializer[Task]):
    class Meta:
        model = Task
        fields = ["slug", "code", "title", "original_title", "problem_type", "from_kep"]


class ProblemSetSerializer(serializers.ModelSerializer[ProblemSet]):
    tasks = TaskRowSerializer(many=True, read_only=True)

    class Meta:
        model = ProblemSet
        fields = ["slug", "title", "description", "tasks"]


class ResultRowSerializer(serializers.ModelSerializer[Result]):
    participant = serializers.CharField(source="participant.slug")
    full_name = serializers.CharField(source="participant.full_name")
    country_code = serializers.CharField(source="participant.country_code")

    class Meta:
        model = Result
        fields = ["participant", "full_name", "country_code", "rank", "score", "medal", "is_local"]


class EventDetailSerializer(EventCardSerializer):
    season = serializers.CharField(source="season.slug")
    sets = ProblemSetSerializer(many=True, read_only=True)
    results = serializers.SerializerMethodField()

    class Meta(EventCardSerializer.Meta):
        fields = [
            *EventCardSerializer.Meta.fields,
            "season",
            "description",
            "mode",
            "platform",
            "organizer",
            "eligibility",
            "resources",
            "sets",
            "results",
        ]

    def get_results(self, event: Event) -> list[dict[str, Any]]:
        rows = [row for row in event.results.all() if row.participant.removed_at is None]
        return list(ResultRowSerializer(rows, many=True).data)


class PracticeHereSerializer(serializers.Serializer[Any]):
    slug = serializers.CharField()
    code = serializers.IntegerField(allow_null=True)
    title = serializers.CharField()


class TaskDetailSerializer(serializers.ModelSerializer[Task]):
    event = serializers.CharField(source="problem_set.event.slug")
    event_title = serializers.CharField(source="problem_set.event.title")
    set_title = serializers.CharField(source="problem_set.title")
    practice_here = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "slug",
            "code",
            "title",
            "original_title",
            "statement",
            "translation_status",
            "problem_type",
            "time_limit_ms",
            "memory_limit_mb",
            "max_score",
            "tags",
            "links",
            "statement_pdf",
            "from_kep",
            "event",
            "event_title",
            "set_title",
            "practice_here",
        ]

    @staticmethod
    def get_practice_here(task: Task) -> list[dict[str, Any]]:
        """Our own copy of the problem, matched by its source (KEP, Codeforces, …)."""
        index = source_key_index()
        ids = [
            index[key]
            for key in {exercise_key(row["url"]) for row in task.links if row.get("url")}
            if key in index
        ]
        return [{"slug": p.slug, "code": p.code, "title": p.title} for p in public_problems(ids)]


class ParticipantResultSerializer(serializers.ModelSerializer[Result]):
    event = serializers.CharField(source="event.slug")
    event_title = serializers.CharField(source="event.title")
    start_date = serializers.DateField(source="event.start_date")

    class Meta:
        model = Result
        fields = ["event", "event_title", "start_date", "rank", "score", "medal"]


class ParticipantSerializer(serializers.ModelSerializer[Participant]):
    results = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ["slug", "full_name", "country_code", "results"]

    def get_results(self, participant: Participant) -> list[dict[str, Any]]:
        rows = participant.results.select_related("event").order_by("-event__start_date")
        return list(ParticipantResultSerializer(rows, many=True).data)


# ── views ────────────────────────────────────────────────────────────────

_VISIBLE_RESULTS = Q(results__participant__removed_at__isnull=True)


class SeasonListView(APIView):
    """Every season with its routes and events, newest first."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: SeasonSerializer(many=True)})
    def get(self, request: Request) -> Response:
        events = Event.objects.annotate(
            task_count=Count(
                "sets__tasks", filter=Q(sets__tasks__removed_at__isnull=True), distinct=True
            ),
            result_count=Count("results", filter=_VISIBLE_RESULTS, distinct=True),
        )
        seasons = Season.objects.prefetch_related(Prefetch("events", queryset=events))
        return Response(SeasonSerializer(seasons, many=True).data)


class EventDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: EventDetailSerializer})
    def get(self, request: Request, slug: str) -> Response:
        event = (
            Event.objects.select_related("season")
            .prefetch_related(
                Prefetch("sets__tasks", queryset=Task.objects.filter(removed_at__isnull=True)),
                Prefetch("results", queryset=Result.objects.select_related("participant")),
            )
            .filter(slug=slug)
            .first()
        )
        if event is None:
            raise Http404
        return Response(EventDetailSerializer(event).data)


class TaskDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: TaskDetailSerializer})
    def get(self, request: Request, slug: str, task: str) -> Response:
        row = (
            Task.objects.select_related("problem_set__event")
            .filter(problem_set__event__slug=slug, slug=task, removed_at__isnull=True)
            .first()
        )
        if row is None:
            raise Http404
        return Response(TaskDetailSerializer(row).data)


class ParticipantView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: ParticipantSerializer})
    def get(self, request: Request, slug: str) -> Response:
        participant = Participant.objects.filter(slug=slug, removed_at__isnull=True).first()
        if participant is None:
            raise Http404
        return Response(ParticipantSerializer(participant).data)
