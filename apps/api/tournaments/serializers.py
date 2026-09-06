from __future__ import annotations

from typing import Any

from rest_framework import serializers

from tournaments.models import Tournament, TournamentStage, TournamentStanding


class StageSerializer(serializers.ModelSerializer[TournamentStage]):
    contest = serializers.SlugRelatedField[Any](slug_field="slug", read_only=True)
    contest_title = serializers.CharField(source="contest.title", read_only=True)
    start_at = serializers.DateTimeField(source="contest.start_at", read_only=True)
    end_at = serializers.DateTimeField(source="contest.end_at", read_only=True)
    is_finished = serializers.BooleanField(source="contest.is_finished", read_only=True)

    class Meta:
        model = TournamentStage
        fields = [
            "order",
            "title",
            "contest",
            "contest_title",
            "start_at",
            "end_at",
            "weight",
            "is_finished",
        ]


class TournamentSerializer(serializers.ModelSerializer[Tournament]):
    stage_count = serializers.IntegerField(read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = Tournament
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "end_at",
            "stage_count",
            "is_running",
            "is_finished",
        ]


class TournamentDetailSerializer(TournamentSerializer):
    stages = StageSerializer(many=True, read_only=True)

    class Meta(TournamentSerializer.Meta):
        fields = [*TournamentSerializer.Meta.fields, "stages"]


class TournamentStandingSerializer(serializers.ModelSerializer[TournamentStanding]):
    username = serializers.CharField(source="user.username", read_only=True)
    display_name = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = TournamentStanding
        fields = ["rank", "username", "display_name", "points", "solved_total", "stages_played"]
