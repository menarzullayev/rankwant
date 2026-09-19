"""Hack API shakllari — ADR-0020.

Ko'rinish qoidasi shu yerda: hack natijasi OMMAVIY (kim kimni sindirdi —
musobaqa jadvalining bir qismi), lekin hackerning O'Z materiali emas.
Generator manbasi, test kiritmasi va xato matni faqat egasiga va
xodimga ko'rinadi: aks holda hack yuborish o'z kodini e'lon qilish
bilan barobar bo'lardi.
"""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from rest_framework import serializers

from contests.models import Contest
from hacks.models import Hack, HackLock
from judging.models import MAX_SOURCE_BYTES, Attempt
from problems.models import Language, Problem
from profiles.titles import TitleField

log = logging.getLogger(__name__)

#: Kiritma sahifada ko'rsatiladi, ya'ni to'liq megabayt kerak emas.
#: Namuna testlar bilan bir xil chegara (`problems.storage`).
INPUT_PREVIEW_BYTES = 16 * 1024


class HackSerializer(serializers.ModelSerializer[Hack]):
    hacker = serializers.CharField(source="hacker.username", read_only=True)
    hacker_title = TitleField(source="hacker")
    defender = serializers.CharField(source="defender_attempt.user.username", read_only=True)
    problem = serializers.SlugRelatedField[Problem](slug_field="slug", read_only=True)
    contest = serializers.SlugRelatedField[Contest](slug_field="slug", read_only=True)
    detail = serializers.SerializerMethodField()

    class Meta:
        model = Hack
        fields = [
            "id",
            "hacker",
            "hacker_title",
            "defender",
            "defender_attempt",
            "problem",
            "contest",
            "policy",
            "status",
            "stage",
            "defender_verdict",
            "detail",
            "points",
            "input_size",
            "created_at",
            "judged_at",
        ]

    def _is_owner(self, hack: Hack) -> bool:
        user = getattr(self.context.get("request"), "user", None)
        if user is None or not user.is_authenticated:
            return False
        return bool(user.pk == hack.hacker_id or user.is_staff)

    def get_detail(self, obj: Hack) -> str:
        """Sabab matni — faqat egasiga.

        Bu yerda validator xabari yoki generatorning kompilyatsiya xatosi
        turadi, ya'ni hackerning o'z kodi haqidagi ma'lumot.
        """
        return obj.detail if self._is_owner(obj) else ""


class HackDetailSerializer(HackSerializer):
    generator_language = serializers.SlugRelatedField[Language](slug_field="code", read_only=True)
    generator_source = serializers.SerializerMethodField()
    test_input = serializers.SerializerMethodField()

    class Meta(HackSerializer.Meta):
        fields = [
            *HackSerializer.Meta.fields,
            "generator_language",
            "generator_source",
            "test_input",
        ]

    def get_generator_source(self, obj: Hack) -> str:
        return obj.generator_source if self._is_owner(obj) else ""

    def get_test_input(self, obj: Hack) -> str:
        """Yuborilgan test — egasiga, boshiga qadar qirqilgan.

        Saqlash yiqilsa bo'sh qaytadi: hack sahifasi butunlay ochilmay
        qolgandan ko'ra kiritmasiz ochilgani yaxshi.
        """
        if not obj.input_ref or not self._is_owner(obj):
            return ""
        from problems import storage

        try:
            data = storage.get_test_data(obj.input_ref)
        except Exception:
            log.warning("hack %s kiritmasi o'qilmadi", obj.pk)
            return ""
        return data[:INPUT_PREVIEW_BYTES]


class HackCreateSerializer(serializers.Serializer[dict[str, Any]]):
    """Hack yuborish: yo tayyor kiritma, YO generator dasturi.

    `trim_whitespace=False` ataylab: test kiritmasida oxirgi qator uzilishi
    ham ma'noga ega va DRF standart holatda uni jimgina yeb qo'yardi.
    """

    attempt = serializers.IntegerField()
    test_input = serializers.CharField(allow_blank=True, default="", trim_whitespace=False)
    generator_language = serializers.SlugField(required=False, allow_null=True)
    generator_source = serializers.CharField(allow_blank=True, default="", trim_whitespace=False)

    def validate_attempt(self, value: int) -> int:
        if not Attempt.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Attempt not found")
        return value

    def validate_test_input(self, value: str) -> str:
        if len(value.encode()) > settings.HACK_INPUT_MAX_BYTES:
            raise serializers.ValidationError(
                f"Input exceeds {settings.HACK_INPUT_MAX_BYTES // 1024} KB — "
                "send a larger case with a generator"
            )
        return value

    def validate_generator_source(self, value: str) -> str:
        if len(value.encode()) > MAX_SOURCE_BYTES:
            raise serializers.ValidationError(
                f"Source exceeds {MAX_SOURCE_BYTES // 1024} KB"
            )
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        code = attrs.get("generator_language")
        has_input = bool(attrs.get("test_input", "").strip())
        if code and has_input:
            raise serializers.ValidationError(
                "Provide either input or a generator, not both"
            )
        if not code and not has_input:
            raise serializers.ValidationError("Test input or a generator is required")

        if code:
            language = Language.objects.filter(code=code, is_active=True).first()
            if language is None:
                raise serializers.ValidationError(
                    {"generator_language": "This language is not supported"}
                )
            if not attrs.get("generator_source", "").strip():
                raise serializers.ValidationError({"generator_source": "Generator source is empty"})
            attrs["generator_language_obj"] = language

        attrs["attempt_obj"] = Attempt.objects.select_related(
            "problem", "language", "contest", "user"
        ).get(pk=attrs["attempt"])
        return attrs


class HackLockSerializer(serializers.ModelSerializer[HackLock]):
    contest = serializers.SlugRelatedField[Contest](slug_field="slug", read_only=True)
    problem = serializers.SlugRelatedField[Problem](slug_field="slug", read_only=True)

    class Meta:
        model = HackLock
        fields = ["id", "contest", "problem", "created_at"]


class HackLockCreateSerializer(serializers.Serializer[dict[str, Any]]):
    contest = serializers.SlugField()
    problem = serializers.SlugField()


class HackEligibilitySerializer(serializers.Serializer[dict[str, Any]]):
    """«Hack qila olamanmi?» javobi.

    Sabab HAR DOIM qaytariladi (ADR-0020, 2-tamoyil): UI tugmani jimgina
    yashirsa, foydalanuvchi nima yetishmayotganini bilmasdi.
    """

    can_hack = serializers.BooleanField(read_only=True)
    reason = serializers.CharField(read_only=True, allow_blank=True)
    policy = serializers.CharField(read_only=True, allow_null=True)
    policy_label = serializers.CharField(read_only=True, allow_blank=True)
    needs_lock = serializers.BooleanField(read_only=True)
    locked = serializers.BooleanField(read_only=True)


class HackRoomSerializer(serializers.Serializer[dict[str, Any]]):
    number = serializers.IntegerField(read_only=True)
    members = serializers.ListField(child=serializers.CharField(), read_only=True)
