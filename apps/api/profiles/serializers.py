from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from django.utils import timezone
from rest_framework import serializers

from core.models import User
from profiles import external
from profiles.catalog import TECHNOLOGIES
from profiles.models import (
    BADGE_COLOR,
    BADGE_TEXT_MAX,
    Education,
    ExternalProfile,
    Skill,
    Team,
    TeamMember,
    UserSkill,
    UserSkillBadge,
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


class _PeriodMixin:
    """Yil + oy. `current=True` yoki tugash yili yo'q — hozirgacha."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        latest = timezone.localdate().year + YEAR_AHEAD
        start, end = attrs.get("start_year"), attrs.get("end_year")
        start_month, end_month = attrs.get("start_month"), attrs.get("end_month")
        for value in (start, end):
            if value is not None and not 1950 <= value <= latest:
                raise serializers.ValidationError({"start_year": "Year is invalid"})
        for month, field in ((start_month, "start_month"), (end_month, "end_month")):
            if month is not None and not 1 <= month <= 12:
                raise serializers.ValidationError({field: "Month must be 1–12"})
        if start_month is not None and start is None:
            raise serializers.ValidationError({"start_month": "A year is required for the month"})
        if end_month is not None and end is None:
            raise serializers.ValidationError({"end_month": "A year is required for the month"})
        if attrs.get("current"):
            attrs["end_year"] = None
            attrs["end_month"] = None
            end = end_month = None
        elif end is None and end_month is None:
            attrs["current"] = False
        start_stamp = None if start is None else start * 12 + (start_month or 1)
        end_stamp = None if end is None else end * 12 + (end_month or 12)
        if start_stamp is not None and end_stamp is not None and end_stamp < start_stamp:
            raise serializers.ValidationError({"end_year": "End is before start"})
        return attrs


class EducationSerializer(_PeriodMixin, serializers.ModelSerializer[Education]):
    class Meta:
        model = Education
        fields = [
            "organization",
            "degree",
            "start_year",
            "start_month",
            "end_year",
            "end_month",
            "current",
        ]


class WorkSerializer(_PeriodMixin, serializers.ModelSerializer[WorkExperience]):
    class Meta:
        model = WorkExperience
        fields = [
            "company",
            "title",
            "start_year",
            "start_month",
            "end_year",
            "end_month",
            "current",
        ]


class SkillBadgeSerializer(serializers.ModelSerializer[UserSkillBadge]):
    class Meta:
        model = UserSkillBadge
        fields = ["text", "icon", "color"]

    def validate_text(self, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise serializers.ValidationError("Text must not be empty")
        if len(cleaned) > BADGE_TEXT_MAX:
            raise serializers.ValidationError(f"At most {BADGE_TEXT_MAX} characters")
        if re.search(r"[\x00-\x1f\x7f]", cleaned):
            raise serializers.ValidationError("The text must not contain control characters")
        return cleaned

    def validate_icon(self, value: str) -> str:
        if value not in TECHNOLOGIES:
            raise serializers.ValidationError("The icon must be chosen from the catalogue")
        return value

    def validate_color(self, value: str) -> str:
        if not re.fullmatch(BADGE_COLOR, value):
            raise serializers.ValidationError("Colour must be #rrggbb")
        return value.lower()


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


class FollowerSerializer(UserMiniSerializer):
    """Obunachilar jadvali — maxfiylik qoidasi bilan (maktab, onlayn holat)."""

    school = serializers.SerializerMethodField()
    last_seen = serializers.SerializerMethodField()

    class Meta(UserMiniSerializer.Meta):
        fields = [*UserMiniSerializer.Meta.fields, "school", "rating_contest", "last_seen"]

    def get_school(self, user: User) -> str:
        if "school" in (user.hidden_fields or []):
            return ""
        return user.school_ref.name if user.school_ref is not None else user.school

    def get_last_seen(self, user: User) -> datetime | None:
        if "online" in (user.hidden_fields or []):
            return None
        value: datetime | None = getattr(user, "last_seen", None)
        return value


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
