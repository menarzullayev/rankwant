from __future__ import annotations

from typing import Any

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from contests.models import (
    Certificate,
    Clarification,
    Contest,
    ContestProblem,
    ContestRegistration,
    Standing,
)
from profiles.titles import TitleField, UserTitleSerializer


class ContestProblemSerializer(serializers.ModelSerializer[ContestProblem]):
    slug = serializers.CharField(source="problem.slug", read_only=True)
    title = serializers.CharField(source="problem.title", read_only=True)

    class Meta:
        model = ContestProblem
        fields = ["index_letter", "slug", "title", "points"]


class ContestSerializer(serializers.ModelSerializer[Contest]):
    is_running = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)
    is_frozen = serializers.BooleanField(read_only=True)
    #: Hack oynasi (ADR-0020) — ikkalasi ham `Contest` xossasi. Ularsiz
    #: mijoz «hack qilsa bo'ladimi va qachongacha?» degan savolga javob
    #: topa olmasdi: oyna vaqt bo'yicha ochiladi va yopiladi.
    is_hack_open = serializers.BooleanField(read_only=True)
    hack_open_until = serializers.DateTimeField(read_only=True)
    #: Registrations, annotated by the viewset — one COUNT for the whole list.
    participant_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Contest
        fields = [
            "slug",
            "title",
            "start_at",
            "end_at",
            "scoring_type",
            "is_rated",
            "is_virtual",
            "freeze_minutes",
            "is_running",
            "is_finished",
            "is_frozen",
            "hack_room",
            "is_hack_open",
            "hack_open_until",
            "participant_count",
        ]


class CrewPersonSerializer(serializers.Serializer[Any]):
    username = serializers.CharField()
    user_title = UserTitleSerializer(allow_null=True)


class CrewSerializer(serializers.Serializer[Any]):
    """Who prepared the contest — told on its page, always (ADR-0055, part 2)."""

    authors = CrewPersonSerializer(many=True)
    testers = CrewPersonSerializer(many=True)
    jury = CrewPersonSerializer(many=True)


class ContestDetailSerializer(ContestSerializer):
    problems = ContestProblemSerializer(many=True, read_only=True)
    problem_count = serializers.SerializerMethodField()
    crew = serializers.SerializerMethodField()

    class Meta(ContestSerializer.Meta):
        fields = [
            *ContestSerializer.Meta.fields,
            "description",
            "problems",
            "problem_count",
            "crew",
        ]

    def get_problem_count(self, contest: Contest) -> int:
        return len(contest.problems.all())

    @extend_schema_field(CrewSerializer)
    def get_crew(self, contest: Contest) -> dict[str, Any]:
        from contests.insiders import crew

        return crew(contest)

    def to_representation(self, contest: Contest) -> dict[str, Any]:
        data = super().to_representation(contest)
        # Until the start a title is a hint and a slug is an address:
        # only the number of problems is told (ADR-0055). The people who
        # prepare the contest read it through the staff and organizer APIs.
        if timezone.now() < contest.start_at:
            data["problems"] = []
        return data


class StandingSerializer(serializers.ModelSerializer[Standing]):
    username = serializers.CharField(source="user.username", read_only=True)
    user_title = TitleField(source="user")

    class Meta:
        model = Standing
        fields = [
            "rank",
            "username",
            "user_title",
            "solved_count",
            "penalty",
            # IOI musobaqasida tartibni AYNAN shu belgilaydi (`_rebuild_ioi`),
            # lekin u yuborilmasdi: ballli jadval faqat to'liq yechilganlar
            # sonini ko'rsatib, 270 ballik ishtirokchini 200 ballikdan
            # ajratmasdi.
            "total_score",
            # Hack bali ALOHIDA ustun (ADR-0020). ACM da u `total_score` ga
            # qo'shilmaydi — u yerda tartib yechilgan masala va jarimadan
            # iborat — ya'ni yuborilmasa umuman ko'rinmasdi.
            "hack_score",
            "hacks_successful",
            "hacks_unsuccessful",
            "last_ac_at",
            # Set on an insider's row: no place, shown with a star
            # (ADR-0055, part 2). `rank` is 0 on such a row.
            "insider_role",
        ]


class ContestViewerSerializer(serializers.Serializer[Any]):
    """The signed-in visitor's own standing with a contest.

    Kept off the contest itself so that the contest stays one answer for
    everybody.
    """

    #: "" for a participant; otherwise the insider role (ADR-0055, part 2).
    role = serializers.CharField()
    registered = serializers.BooleanField()
    #: An insider before the start: the problems are open to them and
    #: what they send is a testing attempt.
    testing = serializers.BooleanField()
    #: Filled while `testing` — nobody else sees them before the start.
    problems = ContestProblemSerializer(many=True)


class RegistrationSerializer(serializers.ModelSerializer[ContestRegistration]):
    class Meta:
        model = ContestRegistration
        fields = ["registered_at", "virtual_start_at"]


class CertificateSerializer(serializers.ModelSerializer[Certificate]):
    username = serializers.CharField(source="user.username", read_only=True)
    contest = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ["id", "name", "username", "contest", "place", "participants", "tier", "issued_at"]

    def get_contest(self, cert: Certificate) -> dict[str, Any]:
        return {
            "slug": cert.contest.slug,
            "title": cert.contest.title,
            "end_at": cert.contest.end_at,
        }


class ClarificationSerializer(serializers.ModelSerializer[Clarification]):
    """One question, answer or announcement (ADR-0055, part 3).

    `author` is filled for the moderators only; everybody else is told
    whether the row is theirs (`mine`) and nothing about whose it is.
    """

    problem = serializers.CharField(source="problem.index_letter", allow_null=True, default=None)
    is_announcement = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Clarification
        fields = [
            "id",
            "problem",
            "question",
            "answer",
            "answer_code",
            "is_public",
            "is_announcement",
            "mine",
            "author",
            "created_at",
            "answered_at",
        ]

    def get_is_announcement(self, row: Clarification) -> bool:
        return row.author_id is None

    def get_mine(self, row: Clarification) -> bool:
        user = getattr(self.context.get("request"), "user", None)
        return bool(user is not None and user.is_authenticated and row.author_id == user.pk)

    def get_author(self, row: Clarification) -> str | None:
        if not self.context.get("moderator") or row.author is None:
            return None
        return row.author.username


class ClarificationListSerializer(serializers.Serializer[Any]):
    #: The viewer answers and announces.
    moderator = serializers.BooleanField()
    #: The viewer may ask now (signed in, contest not over).
    can_ask = serializers.BooleanField()
    #: Questions this viewer may still ask in this contest.
    questions_left = serializers.IntegerField()
    results = ClarificationSerializer(many=True)


class ClarificationAskSerializer(serializers.Serializer[Any]):
    problem = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=3)
    question = serializers.CharField(max_length=4000, trim_whitespace=True)


class ClarificationAnswerSerializer(serializers.Serializer[Any]):
    answer = serializers.CharField(required=False, allow_blank=True, max_length=4000)
    answer_code = serializers.CharField(required=False, allow_blank=True, max_length=16)
    public = serializers.BooleanField(default=False)


class ContestAnnouncementSerializer(serializers.Serializer[Any]):
    problem = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=3)
    text = serializers.CharField(max_length=4000)
