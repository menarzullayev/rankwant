from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from core.models import User
from profiles import external
from profiles.models import (
    Education,
    ExternalProfile,
    Skill,
    Team,
    TeamMember,
    UserSkill,
    WorkExperience,
)
from profiles.titles import TitleField

#: Kelajakdagi yil ham qabul qilinadi — «2027 da bitiraman».
YEAR_AHEAD = 10


class SkillSerializer(serializers.ModelSerializer[Skill]):
    class Meta:
        model = Skill
        fields = ["slug", "name_uz", "name_ru", "name_en"]


class UserSkillInSerializer(serializers.Serializer[None]):
    skill = serializers.SlugField()
    level = serializers.IntegerField(min_value=0, max_value=100)


class UserSkillOutSerializer(serializers.ModelSerializer[UserSkill]):
    skill = serializers.CharField(source="skill.slug")
    name_uz = serializers.CharField(source="skill.name_uz")
    name_ru = serializers.CharField(source="skill.name_ru")
    name_en = serializers.CharField(source="skill.name_en")

    class Meta:
        model = UserSkill
        fields = ["skill", "name_uz", "name_ru", "name_en", "level"]


class _YearsMixin:
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        latest = timezone.localdate().year + YEAR_AHEAD
        start, end = attrs.get("start_year"), attrs.get("end_year")
        for value in (start, end):
            if value is not None and not 1950 <= value <= latest:
                raise serializers.ValidationError({"start_year": "Yil noto'g'ri"})
        if start is not None and end is not None and end < start:
            raise serializers.ValidationError({"end_year": "Tugash yili boshlanishidan oldin"})
        return attrs


class EducationSerializer(_YearsMixin, serializers.ModelSerializer[Education]):
    class Meta:
        model = Education
        fields = ["organization", "degree", "start_year", "end_year"]


class WorkSerializer(_YearsMixin, serializers.ModelSerializer[WorkExperience]):
    class Meta:
        model = WorkExperience
        fields = ["company", "title", "start_year", "end_year"]


class ExternalInSerializer(serializers.Serializer[None]):
    kind = serializers.ChoiceField(choices=ExternalProfile.Kind.choices)
    handle = serializers.CharField(max_length=200)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            attrs["handle"] = external.normalize(attrs["kind"], attrs["handle"])
        except ValueError as exc:
            raise serializers.ValidationError({"handle": str(exc)}) from None
        return attrs


class ExternalOutSerializer(serializers.ModelSerializer[ExternalProfile]):
    class Meta:
        model = ExternalProfile
        fields = ["kind", "handle", "rating", "max_rating", "rank", "fetched_at"]


class UserMiniSerializer(serializers.ModelSerializer[User]):
    title = TitleField()

    class Meta:
        model = User
        fields = ["username", "display_name", "avatar_url", "title"]


class TeamMemberSerializer(serializers.ModelSerializer[TeamMember]):
    username = serializers.CharField(source="user.username")
    display_name = serializers.CharField(source="user.display_name")
    avatar_url = serializers.CharField(source="user.avatar_url")
    title = TitleField(source="user")

    class Meta:
        model = TeamMember
        fields = ["username", "display_name", "avatar_url", "title", "role", "joined_at"]


class TeamSerializer(serializers.ModelSerializer[Team]):
    members = TeamMemberSerializer(many=True, read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "join_code", "created_at", "members", "role"]

    def get_role(self, obj: Team) -> str | None:
        viewer = self.context.get("viewer")
        for member in obj.members.all():
            if viewer is not None and member.user_id == viewer.pk:
                return str(member.role)
        return None


class TeamCreateSerializer(serializers.Serializer[None]):
    name = serializers.CharField(max_length=60)


class TeamJoinSerializer(serializers.Serializer[None]):
    #: Kod yoki to'liq havola.
    code = serializers.CharField(max_length=300)
