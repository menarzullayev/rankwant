"""Staff (admin UI) serializerlari — foydalanuvchilar."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from core.models import User


class StaffUserSerializer(serializers.ModelSerializer[User]):
    """Admin ko'rinishi. Tahrirlanadigan: display_name, bio, is_active, is_staff.

    Parol va login ma'lumotlari bu yuzada YO'Q — admin parolni ko'rmaydi
    ham, o'rnatmaydi ham.
    """

    qvant_balance = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "display_name",
            "bio",
            "is_active",
            "is_staff",
            "is_superuser",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "rating_challenges",
            "qvant_balance",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "is_superuser",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "rating_challenges",
            "date_joined",
            "last_login",
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        instance = self.instance
        actor = self.context["request"].user
        if instance is None:
            return attrs

        # O'zini o'zi bloklash yoki xodimlikdan chiqarish — yagona admin
        # tizimdan qulflanib qolmasligi uchun taqiqlanadi. Forma barcha
        # maydonlarni yuboradi, shuning uchun faqat HAQIQIY o'zgarish tekshiriladi.
        if instance.pk == actor.pk:
            for field in ("is_active", "is_staff"):
                if field in attrs and attrs[field] != getattr(instance, field):
                    raise serializers.ValidationError(
                        {field: "O'z hisobingizning bu maydonini o'zgartira olmaysiz"}
                    )

        if not actor.is_superuser:
            if "is_staff" in attrs and attrs["is_staff"] != instance.is_staff:
                raise serializers.ValidationError(
                    {"is_staff": "Xodim huquqini faqat superuser o'zgartira oladi"}
                )
            # Oddiy xodim boshqa xodimni yoki superuser'ni bloklay olmaydi —
            # aks holda bitta xodim butun boshqaruvni qulflab qo'yardi.
            privileged = instance.is_staff or instance.is_superuser
            if privileged and "is_active" in attrs and attrs["is_active"] != instance.is_active:
                raise serializers.ValidationError(
                    {"is_active": "Xodim yoki superuser hisobini faqat superuser bloklashi mumkin"}
                )
        return attrs


class QvantAdjustSerializer(serializers.Serializer[dict[str, Any]]):
    amount = serializers.IntegerField()
    note = serializers.CharField(max_length=200)

    def validate_amount(self, value: int) -> int:
        if value == 0:
            raise serializers.ValidationError("Miqdor nolga teng bo'lmasligi kerak")
        return value


class StaffNotifySerializer(serializers.Serializer[dict[str, Any]]):
    title = serializers.CharField(max_length=200)
    body = serializers.CharField(allow_blank=True, required=False, default="")
