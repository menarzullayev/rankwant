from __future__ import annotations

from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import serializers

from core import handles
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

    def validate_email(self, value: str) -> str:
        # Profilni tahrirlashda ham tekshiriladi: aks holda band pochtani
        # yozish bazadagi cheklovga urilib 500 berardi.
        if value and _email_taken(value, exclude=self.instance):
            raise serializers.ValidationError("Bu email band")
        return value


def _email_taken(value: str, *, exclude: User | None = None) -> bool:
    """Pochta boshqa hisobda bandmi — registrga qaramay."""
    rows = User.objects.filter(email__iexact=value)
    if exclude is not None:
        rows = rows.exclude(pk=exclude.pk)
    return rows.exists()


class RegisterSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "display_name"]
        # Pochtasiz hisobni tiklab bo'lmaydi: parolni unutgan
        # foydalanuvchining boshqa kanali qolmaydi.
        #
        # `username` uchun validatorlar ATAYIN qayta beriladi: model
        # `unique=True` bo'lgani uchun DRF o'zining `UniqueValidator`
        # ini qo'shadi, u esa pastdagi `validate_username` dan OLDIN
        # ishlab, inglizcha «A user with that username already exists»
        # qaytarardi — ya'ni o'zbekcha matn hech qachon ko'rinmasdi va
        # registrni farqlamaydigan tekshiruv ham o'tkazib yuborilardi.
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
            # Django ning standart validatori o'rniga o'zimizniki: u lotin,
            # kirill, raqam, `_` va `.` ga ruxsat beradi va o'zbekcha maxsus
            # harflarni rad etadi — ADR-0016.
            "username": {"validators": []},
        }

    def validate_email(self, value: str) -> str:
        if _email_taken(value):
            raise serializers.ValidationError("Bu email band")
        return value

    def validate_username(self, value: str) -> str:
        try:
            handles.validate(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages[0]) from None

        # Registr farqi bilan taqlid qilishning oldini oladi: `Aziz` va
        # `aziz` bitta nom hisoblanadi. Reyting va profil obro'ga
        # bog'langan platformada bu xavfsizlik masalasi — o'lchandi,
        # mavjud nomning katta harfli nusxasini olish mumkin edi.
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Bu username band")

        # Ko'zga o'xshash harflar bilan taqlid: kirill va lotinda bir xil
        # ko'rinadigan harflar bor, ya'ni registrsiz tekshiruv yetmaydi.
        if User.objects.filter(username_skeleton=handles.skeleton(value)).exists():
            raise serializers.ValidationError("Bu username mavjud nomga juda o'xshash")
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
            # Nom yoki pochta bandligi serializerda, yozuv esa bazada
            # tekshiriladi — oradagi oynada bir vaqtda kelgan so'rovlar
            # 500 berardi.
            field = "email" if _email_taken(validated_data.get("email", "")) else "username"
            raise serializers.ValidationError(
                {field: "Bu email band" if field == "email" else "Bu username band"}
            ) from None
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


class PasswordResetRequestSerializer(serializers.Serializer[dict[str, Any]]):
    """Tiklash so'rovi — email yoki username bo'yicha."""

    login = serializers.CharField(max_length=254)


class PasswordResetConfirmSerializer(serializers.Serializer[dict[str, Any]]):
    """Tasdiqlash — havola tokeni YOKI (username + kod).

    Ikkala yo'l ham qoladi: havola telefondagi pochtadan kompyuterdagi
    brauzerga o'tmaydi, kod esa o'tadi (ADR-0015).
    """

    token = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True, max_length=6)
    password = serializers.CharField(write_only=True)

    # Parol bu yerda TEKSHIRILMAYDI: `validate_password` ga foydalanuvchi
    # berilishi shart, aks holda `UserAttributeSimilarityValidator` ishlamaydi
    # va parol sifatida username qabul qilinardi (yuqorida o'lchangan).
    # Foydalanuvchi esa faqat token yechilgandan keyin ma'lum bo'ladi —
    # shuning uchun tekshiruv `PasswordResetConfirmView` da.

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("token") and not (attrs.get("username") and attrs.get("code")):
            raise serializers.ValidationError(
                {"token": "Havola tokeni yoki foydalanuvchi nomi bilan kod kerak"}
            )
        return attrs


class SocialLinkSerializer(serializers.Serializer[dict[str, Any]]):
    """Ijtimoiy hisobni mavjud hisobga bog'lash — parol bilan tasdiqlanadi."""

    password = serializers.CharField(write_only=True)
