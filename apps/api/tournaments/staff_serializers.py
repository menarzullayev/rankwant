"""Staff (admin UI) serializerlari — chempionat va bosqichlari.

Bosqichlar alohida endpoint emas: `stages` massivi yuborilsa mavjud
TournamentStage qatorlari TO'LIQ almashtiriladi (PUT uslubi). Yuborilmasa —
tegilmaydi.
"""

from __future__ import annotations

from typing import Any

from django.db import transaction
from rest_framework import serializers

from contests.models import Contest
from tournaments.models import Tournament, TournamentStage


class StaffStageSerializer(serializers.Serializer[TournamentStage]):
    order = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=120)
    contest = serializers.SlugRelatedField[Contest](
        slug_field="slug", queryset=Contest.objects.all()
    )
    contest_title = serializers.CharField(source="contest.title", read_only=True)
    weight = serializers.IntegerField(min_value=1, default=1)


class StaffTournamentSerializer(serializers.ModelSerializer[Tournament]):
    stages = StaffStageSerializer(many=True, required=False)
    stage_count = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "end_at",
            "is_public",
            "created_at",
            "stages",
            "stage_count",
        ]
        read_only_fields = ["created_at"]

    def get_stage_count(self, obj: Tournament) -> int:
        return obj.stages.count()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({"end_at": "The end time must be after the start"})
        if "stages" in attrs:
            self._validate_stages(attrs["stages"])
        return attrs

    def _validate_stages(self, stages: list[dict[str, Any]]) -> None:
        # PATCH da DRF bolalar maydonlarini ham ixtiyoriy qiladi, ya'ni
        # majburiy deb e'lon qilish yetmaydi — indekslashdan oldin
        # tekshirmasak KeyError → 500 bo'lardi.
        missing = [k for k in ("order", "contest") if any(k not in s for s in stages)]
        if missing:
            fields = ", ".join(f"`{m}`" for m in missing)
            raise serializers.ValidationError({"stages": f"Each stage needs {fields}"})
        orders = [s["order"] for s in stages]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError({"stages": "Stage order numbers must be unique"})

        contests: list[Contest] = [s["contest"] for s in stages]
        if len({c.pk for c in contests}) != len(contests):
            raise serializers.ValidationError({"stages": "A contest cannot appear in two stages"})

        # Contest ↔ bosqich OneToOne: boshqa chempionatda band bo'lsa — aniq xato
        taken = TournamentStage.objects.filter(contest__in=contests).select_related(
            "contest", "tournament"
        )
        if self.instance is not None:
            taken = taken.exclude(tournament=self.instance)
        busy = [f"{s.contest.slug} → {s.tournament.slug}" for s in taken]
        if busy:
            raise serializers.ValidationError(
                {"stages": "Contest is already a stage of another championship: " + ", ".join(busy)}
            )

    @staticmethod
    def _replace_stages(tournament: Tournament, stages: list[dict[str, Any]]) -> None:
        TournamentStage.objects.filter(tournament=tournament).delete()
        TournamentStage.objects.bulk_create(
            [TournamentStage(tournament=tournament, **s) for s in stages]
        )

    @transaction.atomic
    def create(self, validated_data: dict[str, Any]) -> Tournament:
        stages = validated_data.pop("stages", [])
        tournament = Tournament.objects.create(**validated_data)
        self._replace_stages(tournament, stages)
        return tournament

    @transaction.atomic
    def update(self, instance: Tournament, validated_data: dict[str, Any]) -> Tournament:
        stages = validated_data.pop("stages", None)
        tournament = super().update(instance, validated_data)
        if stages is not None:
            self._replace_stages(tournament, stages)
        return tournament
