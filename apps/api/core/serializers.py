from __future__ import annotations

import re
from datetime import date
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from core import handles, usernames
from core.models import PRIVACY_FIELDS, ApiToken, User, UserSession
from profiles.catalog import UZ_REGIONS


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


#: Mavzu almashishdagi animatsiya turlari.
UI_EFFECTS = ("none", "fade", "circle")


class MeSerializer(serializers.ModelSerializer[User]):
    #: Ulangan provayderlar — sozlamalar sahifasi shu ro'yxatga qaraydi.
    social = serializers.SerializerMethodField()
    #: Faqat ijtimoiy hisob bilan kirgan odamda parol yo'q — sozlamalar
    #: «almashtirish» o'rniga «o'rnatish» formasini ko'rsatadi.
    has_password = serializers.SerializerMethodField()
    #: Keyingi bepul almashtirish sanasi va pullik narxi.
    username_change = serializers.SerializerMethodField()

    def get_social(self, obj: User) -> list[str]:
        return sorted(obj.social_accounts.values_list("provider", flat=True))

    def get_has_password(self, obj: User) -> bool:
        return obj.has_usable_password()

    def get_username_change(self, obj: User) -> dict[str, Any]:
        free_at = usernames.next_free_at(obj)
        return {"free_at": free_at.isoformat() if free_at else None, "price": usernames.PRICE}

    class Meta:
        model = User
        fields = [
            "id",
            "is_staff",
            "username",
            "email",
            "display_name",
            "email_verified",
            "social",
            "has_password",
            "avatar_url",
            "bio",
            "locale",
            "theme",
            "country",
            "region",
            "school",
            "grade",
            "website",
            "birth_date",
            "hidden_fields",
            "ui_prefs",
            "notify_prefs",
            "username_change",
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
            # Pochta faqat tasdiqlangan almashtirish orqali (`me/email/`),
            # avatar esa faqat yuklash orqali: ixtiyoriy tashqi manzil har
            # profil ko'rilishini uchinchi tomonga bildirardi.
            "email",
            "avatar_url",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "streak_count",
            "streak_freeze_until",
            "date_joined",
        ]

    def validate_country(self, value: str) -> str:
        value = value.upper()
        if value and not re.fullmatch(r"[A-Z]{2}", value):
            raise serializers.ValidationError("Mamlakat kodi noto'g'ri")
        return value

    def validate_birth_date(self, value: date | None) -> date | None:
        if value is not None and (value > timezone.localdate() or value.year < 1900):
            raise serializers.ValidationError("Tug'ilgan sana noto'g'ri")
        return value

    def validate_hidden_fields(self, value: Any) -> list[str]:
        if not isinstance(value, list) or any(v not in PRIVACY_FIELDS for v in value):
            raise serializers.ValidationError("Noma'lum maydon")
        return sorted(set(value))

    def validate_ui_prefs(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise serializers.ValidationError("Obyekt kutilgan")
        for key, item in value.items():
            ok = (
                (key == "style" and isinstance(item, str) and re.fullmatch(r"[a-z-]{1,20}", item))
                or (key == "sound" and isinstance(item, bool))
                or (key == "effect" and item in UI_EFFECTS)
            )
            if not ok:
                raise serializers.ValidationError(f"Noma'lum sozlama: {key}")
        return dict(value)

    def validate_notify_prefs(self, value: Any) -> dict[str, dict[str, bool]]:
        from notifications.models import Notification

        if not isinstance(value, dict):
            raise serializers.ValidationError("Obyekt kutilgan")
        kinds = set(Notification.Kind.values)
        clean: dict[str, dict[str, bool]] = {}
        for kind, channels in value.items():
            if kind not in kinds or not isinstance(channels, dict):
                raise serializers.ValidationError(f"Noma'lum tur: {kind}")
            if set(channels) - {"site", "telegram"} or not all(
                isinstance(v, bool) for v in channels.values()
            ):
                raise serializers.ValidationError(f"Noto'g'ri kanal: {kind}")
            clean[kind] = dict(channels)
        return clean

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        country = attrs.get("country", self.instance.country if self.instance else "")
        region = attrs.get("region", self.instance.region if self.instance else "")
        # O'zbekistonda viloyat ro'yxatdan — viloyat bo'yicha reyting shunga tayanadi.
        if country == "UZ" and region and region not in UZ_REGIONS:
            raise serializers.ValidationError({"region": "Viloyat ro'yxatdan tanlanadi"})
        return attrs


def _email_taken(value: str, *, exclude: User | None = None) -> bool:
    """Pochta boshqa hisobda bandmi — registrga qaramay."""
    rows = User.objects.filter(email__iexact=value)
    if exclude is not None:
        rows = rows.exclude(pk=exclude.pk)
    return rows.exists()


class EmailVerifySerializer(serializers.Serializer[None]):
    """Havola yoki `username` + kod. Ikkalasi ham bo'lmasa `consume` rad etadi."""

    token = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)


class UsernameCheckSerializer(serializers.Serializer[None]):
    """Yozayotgandagi javob. `reason` bo'sh bo'lsa nom bo'sh."""

    available = serializers.BooleanField()
    reason = serializers.CharField(allow_blank=True)


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
        # Nomini almashtirgan odamning eski nomi 90 kun band — aks holda
        # yangi egasi eski egasining obro'si bilan standings'da tura olardi.
        if usernames.reserved(value):
            raise serializers.ValidationError(
                "Bu nom yaqinda boshqa foydalanuvchiga tegishli bo'lgan"
            )
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


class PasswordChangeSerializer(serializers.Serializer[None]):
    #: Paroli yo'q hisobda (faqat ijtimoiy kirish) bo'sh qoladi.
    old_password = serializers.CharField(required=False, allow_blank=True, write_only=True)
    new_password = serializers.CharField(write_only=True)


class EmailChangeSerializer(serializers.Serializer[None]):
    email = serializers.EmailField()
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)


class UsernameChangeSerializer(serializers.Serializer[None]):
    username = serializers.CharField(max_length=150)
    #: Bepul almashtirish ishlatilgan bo'lsa — Qvant bilan to'lashga rozilik.
    pay = serializers.BooleanField(required=False, default=False)


class UserSessionSerializer(serializers.ModelSerializer[UserSession]):
    current = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = ["id", "user_agent", "ip", "created_at", "last_seen", "current"]

    def get_current(self, obj: UserSession) -> bool:
        return obj.session_key == self.context.get("current_key")


class AvatarImportSerializer(serializers.Serializer[None]):
    provider = serializers.ChoiceField(choices=["google", "github", "telegram"])
