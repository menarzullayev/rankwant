"""Staff (admin UI) serializerlari — musobaqa va uning masalalari."""

from __future__ import annotations

import logging
from typing import Any

from django.apps import apps
from rest_framework import serializers

from contests.insiders import notify_new_testers
from contests.models import Contest, ContestProblem, Organization
from core.models import User
from problems.models import Problem
from problems.readiness import GRADED_READY, enforcing, graded_gate_error

log = logging.getLogger(__name__)


class StaffContestProblemSerializer(serializers.ModelSerializer[ContestProblem]):
    """`PUT staff/contests/<slug>/problems/` ro'yxatining bitta elementi."""

    problem = serializers.SlugRelatedField(slug_field="slug", queryset=Problem.objects.all())
    title = serializers.CharField(source="problem.title", read_only=True)

    class Meta:
        model = ContestProblem
        fields = ["problem", "index_letter", "points", "title"]
        extra_kwargs = {"points": {"required": False}}


def crew_field() -> serializers.SlugRelatedField[User]:
    """A list of people by username — testers, jury (ADR-0055, part 2)."""
    return serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(is_active=True),
        many=True,
        required=False,
    )


def clean_logo(value: str) -> str:
    """A logo is a site path or an https URL — nothing a browser would run
    (ADR-0063 § 2.7; the same rule as team photos)."""
    value = value.strip()
    if not value:
        return value
    site_path = value.startswith("/") and not value.startswith("//")
    if not (site_path or value.startswith("https://")):
        raise serializers.ValidationError("Use a site path (/partners/logo.png) or an https:// URL")
    return value


def clean_https(value: str) -> str:
    value = value.strip()
    if value and not value.startswith("https://"):
        raise serializers.ValidationError("Use an https:// URL")
    return value


class StaffOrganizationSerializer(serializers.ModelSerializer[Organization]):
    contest_count = serializers.IntegerField(source="contests.count", read_only=True)

    class Meta:
        model = Organization
        fields = ["id", "slug", "name", "kind", "logo_url", "website", "about", "contest_count"]

    def validate_logo_url(self, value: str) -> str:
        return clean_logo(value)

    def validate_website(self, value: str) -> str:
        return clean_https(value)


class StaffContestSerializer(serializers.ModelSerializer[Contest]):
    mirror_of = serializers.SlugRelatedField(
        slug_field="slug", queryset=Contest.objects.all(), allow_null=True, required=False
    )
    #: An olympiad archive event (ADR-0063 § 2.4). Looked up through the app
    #: registry, so `contests` does not import `olympiads.models`.
    mirror_of_event = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=apps.get_model("olympiads", "Event")._default_manager.all(),
        allow_null=True,
        required=False,
    )
    partner = serializers.SlugRelatedField(
        slug_field="slug", queryset=Organization.objects.all(), allow_null=True, required=False
    )
    #: Insiders the staff appoint (ADR-0055, part 2). They see the problems
    #: early and take part unrated.
    testers = crew_field()
    jury = crew_field()
    #: Who drafted the contest in `/studio/contests` — read-only here: staff
    #: see whose draft they are publishing.
    organizers = serializers.SlugRelatedField[User](
        slug_field="username", many=True, read_only=True
    )
    problems = StaffContestProblemSerializer(many=True, read_only=True)
    is_running = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = Contest
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "end_at",
            "freeze_minutes",
            "scoring_type",
            "is_rated",
            "is_virtual",
            "is_public",
            "mirror_of",
            "mirror_of_event",
            "partner",
            "prizes",
            "official_title",
            "official_url",
            "ratings_applied_at",
            "created_at",
            "problems",
            "is_running",
            "is_finished",
            "testers",
            "jury",
            "organizers",
        ]
        read_only_fields = ["ratings_applied_at", "created_at"]

    def create(self, validated_data: dict[str, Any]) -> Contest:
        contest = super().create(validated_data)
        notify_new_testers(contest, set())
        return contest

    def update(self, instance: Contest, validated_data: dict[str, Any]) -> Contest:
        before = set(instance.testers.values_list("pk", flat=True))
        contest = super().update(instance, validated_data)
        notify_new_testers(contest, before)
        return contest

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "The end time must be after the start"})
        mirror = attrs.get("mirror_of")
        if mirror is not None and self.instance is not None and mirror.pk == self.instance.pk:
            raise serializers.ValidationError({"mirror_of": "A contest cannot be its own mirror"})

        # A mirror's problems were set elsewhere first: never rated
        # (ADR-0063 § 2.6; the database refuses it too).
        def current(name: str) -> Any:
            return attrs[name] if name in attrs else getattr(self.instance, name, None)

        mirrors = current("mirror_of") is not None or current("mirror_of_event") is not None
        if mirrors and current("is_rated"):
            raise serializers.ValidationError({"is_rated": "A mirror contest is never rated"})
        return attrs

    def validate_official_url(self, value: str) -> str:
        return clean_https(value)


class StaffContestProblemListSerializer(serializers.Serializer[Any]):
    """Masalalar ro'yxatini to'liq almashtirish uchun kirish."""

    problems = StaffContestProblemSerializer(many=True)

    def validate_problems(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        letters = [row["index_letter"] for row in value]
        if len(letters) != len(set(letters)):
            raise serializers.ValidationError("Index letters must be unique")
        slugs = [row["problem"].pk for row in value]
        if len(slugs) != len(set(slugs)):
            raise serializers.ValidationError("A problem cannot be added twice")
        # D8-F (ADR-0037, ADR 0049) — only `validated` content enters a graded
        # contest. This is the first of two layers; `staff_views.py` repeats
        # the same condition, so removing either one alone does not open the
        # gate (`check_negative.py`'s mutation proof removes both).
        for row in value:
            if row["problem"].readiness != GRADED_READY:
                message = graded_gate_error(row["problem"])
                # ADR 0050 — staged rollout: report while the flag is off.
                if not enforcing():
                    log.warning("readiness gate NOT enforced: %s", message)
                    continue
                raise serializers.ValidationError(message)
        return value
