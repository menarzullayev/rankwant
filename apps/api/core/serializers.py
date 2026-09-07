from __future__ import annotations

from typing import Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import ApiToken, User


class UserPublicSerializer(serializers.ModelSerializer[User]):
    """Ommaviy profil.

    ADR-0006 fazali ochilish: Skills va Contests — Phase 0, Activity —
    Phase 1, Challenges — Phase 3 (duel qurilgach yoqildi).
    """

    class Meta:
        model = User
        fields = [
            "username",
            "display_name",
            "avatar_url",
            "bio",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "rating_challenges",
            "streak_count",
            "date_joined",
        ]


class MeSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "display_name",
            "avatar_url",
            "bio",
            "locale",
            "theme",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "streak_count",
            "streak_freeze_until",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "username",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "streak_count",
            "streak_freeze_until",
            "date_joined",
        ]


class RegisterSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "display_name"]

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer[dict[str, Any]]):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ApiTokenSerializer(serializers.ModelSerializer[ApiToken]):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = ApiToken
        fields = [
            "id",
            "name",
            "prefix",
            "scopes",
            "expires_at",
            "last_used_at",
            "revoked_at",
            "created_at",
            "is_active",
        ]
        read_only_fields = ["id", "prefix", "last_used_at", "revoked_at", "created_at"]


class ApiTokenCreateSerializer(serializers.Serializer[dict[str, Any]]):
    name = serializers.CharField(max_length=100)
    scopes = serializers.ListField(
        child=serializers.ChoiceField(choices=ApiToken.Scope.choices),
        allow_empty=False,
    )
    expires_at = serializers.DateTimeField()
