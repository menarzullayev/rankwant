"""Updates API serializerlari.

Til qoidasi: `title`/`body` so'ralgan tilga mos tarjimadan olinadi. Tarjima
bo'lmasa **kanonik o'zbekcha matn** qaytadi — bo'sh maydon emas. Sabab:
tarjima hali tayyor bo'lmagan yangilik ham o'qilishi kerak, va bo'sh sarlavha
ro'yxatni buzadi.
"""

from __future__ import annotations

from typing import Any

from django.utils.translation import get_language
from rest_framework import serializers

from updates.models import SOURCE_LOCALE, SystemUpdate, SystemUpdateTranslation, UpdateRead


def resolve_locale(request: Any = None) -> str:
    """So'ralgan til. `?lang=` ustun, keyin `LocaleMiddleware` qiymati."""
    if request is not None:
        explicit = request.query_params.get("lang")
        if explicit:
            return str(explicit)[:5]
    return str(get_language() or SOURCE_LOCALE)[:5]


class SystemUpdateSerializer(serializers.ModelSerializer[SystemUpdate]):
    """Ochiq o'qish — mehmon ham ko'radi (qaror 8-savol)."""

    title = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    is_actionable = serializers.BooleanField(read_only=True)
    is_read = serializers.SerializerMethodField()
    is_translated = serializers.SerializerMethodField()

    class Meta:
        model = SystemUpdate
        fields = [
            "id",
            "kind",
            "module",
            # `status` — batafsil sahifa nashrdan olinganini aytishi uchun.
            # Ro'yxatda u har doim `published` bo'ladi, ya'ni bu maydon
            # lentani o'zgartirmaydi.
            "status",
            "version",
            "title",
            "body",
            "image",
            "released_at",
            "published_at",
            "source_url",
            "is_actionable",
            "is_read",
            "is_translated",
        ]

    def _translation(self, obj: SystemUpdate) -> SystemUpdateTranslation | None:
        locale = self.context.get("locale") or SOURCE_LOCALE
        if locale == obj.locale:
            return None
        # `prefetch_related("translations")` bo'lsa qayta so'rov ketmaydi.
        for tr in obj.translations.all():
            if tr.locale == locale:
                return tr
        return None

    def get_title(self, obj: SystemUpdate) -> str:
        tr = self._translation(obj)
        return tr.title if tr else obj.title

    def get_body(self, obj: SystemUpdate) -> str:
        tr = self._translation(obj)
        return tr.body if tr else obj.body

    def get_is_translated(self, obj: SystemUpdate) -> bool:
        return self._translation(obj) is not None

    def get_is_read(self, obj: SystemUpdate) -> bool | None:
        """`None` — mehmon. Mehmon uchun o'qilmagan holat yo'q (qaror 8-savol)."""
        user = getattr(self.context.get("request"), "user", None)
        if user is None or not user.is_authenticated:
            return None
        read_ids = self.context.get("read_ids")
        if read_ids is not None:
            return obj.pk in read_ids
        return UpdateRead.objects.filter(user=user, update=obj).exists()


class SystemUpdateTranslationSerializer(serializers.ModelSerializer[SystemUpdateTranslation]):
    class Meta:
        model = SystemUpdateTranslation
        fields = ["locale", "title", "body", "is_machine", "updated_at"]


class StaffSystemUpdateSerializer(serializers.ModelSerializer[SystemUpdate]):
    """Staff yozadi. Tarjimalar ichma-ich keladi (10 til bir yozuvda)."""

    translations = SystemUpdateTranslationSerializer(many=True, required=False)
    author = serializers.CharField(source="author.username", read_only=True, default=None)

    class Meta:
        model = SystemUpdate
        fields = [
            "id",
            "kind",
            "module",
            "status",
            "version",
            "title",
            "body",
            "locale",
            "image",
            "source_repo",
            "source_refs",
            "source_url",
            "released_at",
            "published_at",
            "is_enabled",
            "author",
            "translations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["published_at", "created_at", "updated_at"]

    def _sync_translations(self, instance: SystemUpdate, rows: list[dict[str, Any]]) -> None:
        for row in rows:
            SystemUpdateTranslation.objects.update_or_create(
                update=instance,
                locale=row["locale"],
                defaults={
                    "title": row.get("title", ""),
                    "body": row.get("body", ""),
                    "is_machine": row.get("is_machine", True),
                },
            )

    def create(self, validated_data: dict[str, Any]) -> SystemUpdate:
        rows = validated_data.pop("translations", [])
        instance = super().create(validated_data)
        self._sync_translations(instance, rows)
        return instance

    def update(self, instance: SystemUpdate, validated_data: dict[str, Any]) -> SystemUpdate:
        rows = validated_data.pop("translations", None)
        instance = super().update(instance, validated_data)
        if rows is not None:
            self._sync_translations(instance, rows)
        return instance


class UpdateMarkReadSerializer(serializers.Serializer[dict[str, Any]]):
    """Nom `notifications.MarkReadSerializer` bilan to'qnashmasligi kerak.

    drf-spectacular komponent nomini sinf nomidan oladi: ikkalasi ham
    `MarkRead` bo'lsa sxemada bitta komponent qoladi va noto'g'ri
    hujjat chiqadi. O'lchandi — generatsiya ogohlantirish bergan edi.
    """

    #: Bo'sh bo'lsa — hammasi o'qilgan deb belgilanadi ("Hammasi o'qildi").
    ids = serializers.ListField(child=serializers.IntegerField(), required=False)


class UnreadModuleSerializer(serializers.Serializer[dict[str, Any]]):
    """Nav chipi uchun: qaysi modulda nechta o'qilmagan yozuv bor."""

    module = serializers.CharField()
    count = serializers.IntegerField()
