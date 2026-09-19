"""Staff (admin UI) serializerlari — musobaqa va uning masalalari."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from contests.models import Contest, ContestProblem
from problems.models import Problem


class StaffContestProblemSerializer(serializers.ModelSerializer[ContestProblem]):
    """`PUT staff/contests/<slug>/problems/` ro'yxatining bitta elementi."""

    problem = serializers.SlugRelatedField(slug_field="slug", queryset=Problem.objects.all())
    title = serializers.CharField(source="problem.title", read_only=True)

    class Meta:
        model = ContestProblem
        fields = ["problem", "index_letter", "points", "title"]
        extra_kwargs = {"points": {"required": False}}


class StaffContestSerializer(serializers.ModelSerializer[Contest]):
    mirror_of = serializers.SlugRelatedField(
        slug_field="slug", queryset=Contest.objects.all(), allow_null=True, required=False
    )
    problems = StaffContestProblemSerializer(many=True, read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = Contest
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "end_at",
            "freeze_minutes",
            "scoring_type",
            "is_rated",
            "is_virtual",
            "is_public",
            "mirror_of",
            "ratings_applied_at",
            "created_at",
            "problems",
            "is_running",
            "is_finished",
        ]
        read_only_fields = ["ratings_applied_at", "created_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "The end time must be after the start"})
        mirror = attrs.get("mirror_of")
        if mirror is not None and self.instance is not None and mirror.pk == self.instance.pk:
            raise serializers.ValidationError({"mirror_of": "A contest cannot be its own mirror"})
        return attrs


class StaffContestProblemListSerializer(serializers.Serializer[Any]):
    """Masalalar ro'yxatini to'liq almashtirish uchun kirish."""

    problems = StaffContestProblemSerializer(many=True)

    def validate_problems(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        letters = [row["index_letter"] for row in value]
        if len(letters) != len(set(letters)):
            raise serializers.ValidationError("Index letters must be unique")
        slugs = [row["problem"].pk for row in value]
        if len(slugs) != len(set(slugs)):
            raise serializers.ValidationError("A problem cannot be added twice")
        return value
