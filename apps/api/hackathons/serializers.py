from __future__ import annotations

from typing import Any

from rest_framework import serializers

from hackathons.models import Hackathon, HackathonSubmission


class HackathonSerializer(serializers.ModelSerializer[Hackathon]):
    submission_count = serializers.IntegerField(read_only=True)
    accepts_submissions = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = Hackathon
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "submission_deadline",
            "end_at",
            "submission_count",
            "accepts_submissions",
            "is_finished",
        ]


class SubmissionSerializer(serializers.ModelSerializer[HackathonSubmission]):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = HackathonSubmission
        fields = [
            "id",
            "username",
            "team_name",
            "title",
            "description",
            "repo_url",
            "demo_url",
            "submitted_at",
            "score",
            "feedback",
        ]


class SubmitSerializer(serializers.Serializer[dict[str, Any]]):
    team_name = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    repo_url = serializers.URLField()
    demo_url = serializers.URLField(required=False, allow_blank=True, default="")


class ScoreSerializer(serializers.Serializer[dict[str, Any]]):
    score = serializers.IntegerField(min_value=0, max_value=100)
    feedback = serializers.CharField(required=False, allow_blank=True, default="")
