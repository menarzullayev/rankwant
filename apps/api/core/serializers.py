from __future__ import annotations

from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from rest_framework import serializers

from core.models import ApiToken, User


class UserPublicSerializer(serializers.ModelSerializer[User]):
    """Ommaviy profil.

    ADR-0006 fazali ochilish: Skills va Contests — Phase 0, Activity —
    Phase 1, Challenges — Phase 3 (duel qurilgach yoqildi).
    """

    ranks = serializers.SerializerMethodField()
    max_ratings = serializers.SerializerMethodField()
    solved_by_level = serializers.SerializerMethodField()

    def get_ranks(self, user: User) -> dict[str, int]:
        """Har reyting bo'yicha o'rin.

        Raqamning o'zi «ko'p yoki oz» ekanini aytmaydi — 800 yaxshimi
        yoki yomonmi, faqat boshqalar bilan solishtirganda ma'lum
        bo'ladi. KEP profilida ham har reyting yonida o'rin turadi.

        Faqat detal javobida hisoblanadi: leaderboard'da har qatorga
        to'rtta COUNT qo'shilib ketardi.
        """
        if self.context.get("view") and getattr(self.context["view"], "action", "") != "retrieve":
            return {}
        active = User.objects.filter(is_active=True)
        return {
            name: active.filter(**{f"{field}__gt": getattr(user, field)}).count() + 1
            for name, field in (
                ("skills", "rating_skills"),
                ("contest", "rating_contest"),
                ("activity", "rating_activity"),
                ("challenges", "rating_challenges"),
            )
        }

    def get_max_ratings(self, user: User) -> dict[str, int]:
        """Erishilgan eng yuqori qiymat — hozirgisi tushib ketgan bo'lsa ham."""
        if self.context.get("view") and getattr(self.context["view"], "action", "") != "retrieve":
            return {}
        from django.db.models import Max

        from ratings.models import RatingHistory

        rows = (
            RatingHistory.objects.filter(user=user)
            .values("rating_type")
            .annotate(top=Max("value_after"))
        )
        return {row["rating_type"]: row["top"] for row in rows}

    def get_solved_by_level(self, user: User) -> list[dict[str, Any]]:
        """Daraja kesimida yechilganlar — KEP profilidagi taqsimot.

        Bitta Skills raqami «qayerda turibman» degan savolga javob
        beradi, bu esa «nimani mashq qilishim kerak» degan savolga.
        """
        if self.context.get("view") and getattr(self.context["view"], "action", "") != "retrieve":
            return []
        from collections import Counter

        from problems.models import DIFFICULTY_LEVELS, difficulty_level
        from ratings.models import UserSolvedProblem

        counts: Counter[str] = Counter()
        for value in UserSolvedProblem.objects.filter(
            user=user, problem__is_public=True
        ).values_list("problem__difficulty", flat=True):
            counts[difficulty_level(value)[0]] += 1
        return [
            {"code": code, "label": label, "solved": counts[code]}
            for _, code, label in DIFFICULTY_LEVELS
        ]

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
            "ranks",
            "max_ratings",
            "solved_by_level",
        ]


class MeSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = [
            "id",
            "is_staff",
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
            "is_staff",
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

    def validate_username(self, value: str) -> str:
        # Registr farqi bilan taqlid qilishning oldini oladi: `Aziz` va
        # `aziz` bitta nom hisoblanadi. Reyting va profil obro'ga
        # bog'langan platformada bu xavfsizlik masalasi — o'lchandi,
        # mavjud nomning katta harfli nusxasini olish mumkin edi.
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Bu username band")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # `validate_password` ga foydalanuvchi BERILISHI shart: usiz
        # `UserAttributeSimilarityValidator` umuman ishlamaydi va parol
        # sifatida username ni kiritish qabul qilinardi (o'lchandi).
        validate_password(
            attrs["password"],
            User(
                username=attrs.get("username", ""),
                email=attrs.get("email", ""),
                display_name=attrs.get("display_name", ""),
            ),
        )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            # Nom bandligi serializerda, yozuv esa bazada tekshiriladi —
            # oradagi oynada bir vaqtda kelgan so'rovlar 500 berardi.
            raise serializers.ValidationError({"username": "Bu username band"}) from None
        return user


class LoginSerializer(serializers.Serializer[dict[str, Any]]):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AccountDeleteSerializer(serializers.Serializer[dict[str, Any]]):
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
