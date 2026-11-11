from __future__ import annotations

from typing import Any

from rest_framework import serializers

from coaching.models import CoachLink


class PersonSerializer(serializers.Serializer[Any]):
    username = serializers.CharField()
    display_name = serializers.CharField()


class CoachLinkSerializer(serializers.ModelSerializer[CoachLink]):
    """One link, seen by either side."""

    coach = PersonSerializer(read_only=True)
    student = PersonSerializer(read_only=True)

    class Meta:
        model = CoachLink
        fields = ["id", "coach", "student", "status", "can_view_attempts", "created_at"]
        read_only_fields = fields


class CoachLinksSerializer(serializers.Serializer[Any]):
    #: Links where the reader is the student (pending and active).
    coaches = CoachLinkSerializer(many=True)
    #: Pending links where the reader is the coach.
    requests = CoachLinkSerializer(many=True)


class AskSerializer(serializers.Serializer[Any]):
    coach = serializers.CharField(max_length=150)


class ConsentSerializer(serializers.Serializer[Any]):
    can_view_attempts = serializers.BooleanField()


class RecommendSerializer(serializers.Serializer[Any]):
    #: A slug or an archive number (`123` or `#123`).
    problem = serializers.CharField(max_length=100)
    note = serializers.CharField(max_length=300, required=False, allow_blank=True, default="")


class RecommendationSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    coach = serializers.CharField()
    problem = serializers.CharField()
    problem_title = serializers.CharField()
    note = serializers.CharField()
    solved = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class RecentAttemptSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    problem = serializers.CharField()
    problem_title = serializers.CharField()
    language = serializers.CharField()
    verdict = serializers.CharField()
    in_contest = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class RecommendedSerializer(serializers.Serializer[Any]):
    problem = serializers.CharField()
    problem_title = serializers.CharField()
    solved = serializers.BooleanField()


class CoachStudentSerializer(serializers.Serializer[Any]):
    link = serializers.IntegerField()
    username = serializers.CharField()
    display_name = serializers.CharField()
    can_view_attempts = serializers.BooleanField()
    solved_count = serializers.IntegerField()
    rating_skills = serializers.IntegerField()
    streak = serializers.IntegerField()
    recent = RecentAttemptSerializer(many=True)
    recommended = RecommendedSerializer(many=True)
