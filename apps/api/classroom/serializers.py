from __future__ import annotations

from typing import Any

from rest_framework import serializers

from classroom.models import Assignment, Classroom, ClassroomMember
from problems.models import Problem


class ClassroomMemberSerializer(serializers.ModelSerializer[ClassroomMember]):
    username = serializers.CharField(source="user.username", read_only=True)
    rating_skills = serializers.IntegerField(source="user.rating_skills", read_only=True)

    class Meta:
        model = ClassroomMember
        fields = ["username", "role", "rating_skills", "joined_at"]


class ClassroomSerializer(serializers.ModelSerializer[Classroom]):
    owner = serializers.CharField(source="owner.username", read_only=True)
    member_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Classroom
        fields = ["slug", "name", "description", "owner", "member_count", "created_at"]


class ClassroomOwnerSerializer(ClassroomSerializer):
    """Egasi uchun — qo'shilish kodi ko'rinadi."""

    members = ClassroomMemberSerializer(many=True, read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = [*ClassroomSerializer.Meta.fields, "join_code", "is_active", "members"]


class ClassroomCreateSerializer(serializers.ModelSerializer[Classroom]):
    class Meta:
        model = Classroom
        fields = ["slug", "name", "description"]


class JoinSerializer(serializers.Serializer[dict[str, Any]]):
    join_code = serializers.CharField(max_length=12)


class AssignmentSerializer(serializers.ModelSerializer[Assignment]):
    problems = serializers.SlugRelatedField[Problem](many=True, read_only=True, slug_field="slug")

    class Meta:
        model = Assignment
        fields = ["id", "title", "description", "problems", "due_at", "created_at"]


class AssignmentCreateSerializer(serializers.Serializer[dict[str, Any]]):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    problems = serializers.ListField(child=serializers.SlugField(), allow_empty=False)
    due_at = serializers.DateTimeField(required=False, allow_null=True)
