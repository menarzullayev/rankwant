from __future__ import annotations

from rest_framework import serializers

from contests.models import Contest, ContestProblem, ContestRegistration, Standing


class ContestProblemSerializer(serializers.ModelSerializer[ContestProblem]):
    slug = serializers.CharField(source="problem.slug", read_only=True)
    title = serializers.CharField(source="problem.title", read_only=True)

    class Meta:
        model = ContestProblem
        fields = ["index_letter", "slug", "title", "points"]


class ContestSerializer(serializers.ModelSerializer[Contest]):
    is_running = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)
    is_frozen = serializers.BooleanField(read_only=True)

    class Meta:
        model = Contest
        fields = [
            "slug",
            "title",
            "start_at",
            "end_at",
            "scoring_type",
            "is_rated",
            "is_virtual",
            "freeze_minutes",
            "is_running",
            "is_finished",
            "is_frozen",
        ]


class ContestDetailSerializer(ContestSerializer):
    problems = ContestProblemSerializer(many=True, read_only=True)

    class Meta(ContestSerializer.Meta):
        fields = [*ContestSerializer.Meta.fields, "description", "problems"]


class StandingSerializer(serializers.ModelSerializer[Standing]):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Standing
        fields = ["rank", "username", "solved_count", "penalty", "last_ac_at"]


class RegistrationSerializer(serializers.ModelSerializer[ContestRegistration]):
    class Meta:
        model = ContestRegistration
        fields = ["registered_at", "virtual_start_at"]
