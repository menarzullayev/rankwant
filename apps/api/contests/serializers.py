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
    Organization,
    Standing,
)
from profiles.titles import TitleField, UserTitleSerializer


class ContestProblemSerializer(serializers.ModelSerializer[ContestProblem]):
    slug = serializers.CharField(source="problem.slug", read_only=True)
    title = serializers.CharField(source="problem.title", read_only=True)

    class Meta:
        model = ContestProblem
        fields = ["index_letter", "slug", "title", "points"]


class OrganizationBriefSerializer(serializers.ModelSerializer[Organization]):
    """A partner as the contest list names it (ADR-0063)."""

    class Meta:
        model = Organization
        fields = ["slug", "name", "kind", "logo_url"]


class OrganizationSerializer(OrganizationBriefSerializer):
    """A partner on its contest's page."""

    class Meta(OrganizationBriefSerializer.Meta):
        fields = [*OrganizationBriefSerializer.Meta.fields, "website", "about"]


class MirrorSourceSerializer(serializers.Serializer[Any]):
    """What a mirror contest mirrors: a RankWant contest or an olympiad
    archive event (ADR-0063 § 2.4)."""

    kind = serializers.ChoiceField(choices=["contest", "olympiad"])
    slug = serializers.CharField()
    title = serializers.CharField()


class MirrorSerializer(serializers.Serializer[Any]):
    slug = serializers.CharField()
    title = serializers.CharField()
    start_at = serializers.DateTimeField()


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
    #: Partner, official and mirror marks (ADR-0063).
    partner = OrganizationBriefSerializer(read_only=True, allow_null=True)
    is_mirror = serializers.BooleanField(read_only=True)

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
            "partner",
            "official_title",
            "is_mirror",
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
    partner = OrganizationSerializer(read_only=True, allow_null=True)
    mirror_source = serializers.SerializerMethodField()
    mirrors = serializers.SerializerMethodField()

    class Meta(ContestSerializer.Meta):
        fields = [
            *ContestSerializer.Meta.fields,
            "description",
            "problems",
            "problem_count",
            "crew",
            "prizes",
            "official_url",
            "mirror_source",
            "mirrors",
        ]

    @extend_schema_field(MirrorSourceSerializer(allow_null=True))
    def get_mirror_source(self, contest: Contest) -> dict[str, Any] | None:
        """The original, when it can be shown: a hidden contest is not named."""
        original = contest.mirror_of
        if original is not None and original.is_public:
            return {"kind": "contest", "slug": original.slug, "title": original.title}
        event = contest.mirror_of_event
        if event is not None:
            return {"kind": "olympiad", "slug": event.slug, "title": event.title}
        return None

    @extend_schema_field(MirrorSerializer(many=True))
    def get_mirrors(self, contest: Contest) -> list[dict[str, Any]]:
        rows = contest.mirrors.filter(is_public=True).order_by("start_at")
        return [{"slug": c.slug, "title": c.title, "start_at": c.start_at} for c in rows]

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
    #: The place among the region's official rows; only in a regional
    #: table (`?region=`, contests.regional). `null` in the full one.
    region_rank = serializers.SerializerMethodField()

    def get_region_rank(self, row: Standing) -> int | None:
        return getattr(row, "region_rank", None)

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
            # Disqualified by the jury (part 4): «DQ», no place.
            "is_disqualified",
            "region_rank",
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
    #: The jury's reason, when the viewer was disqualified (part 4).
    disqualified_reason = serializers.CharField(allow_null=True)
    #: The viewer reads the fair-play report and disqualifies.
    judge = serializers.BooleanField()


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


class IntegrityRowSerializer(serializers.Serializer[Any]):
    """One attempt whose editor signals stand out (ADR-0055, part 4)."""

    attempt = serializers.IntegerField()
    username = serializers.CharField()
    problem = serializers.CharField()
    verdict = serializers.CharField()
    created_at = serializers.DateTimeField()
    flags = serializers.ListField(child=serializers.CharField())
    source_chars = serializers.IntegerField()
    pasted_chars = serializers.IntegerField()
    largest_paste = serializers.IntegerField()
    paste_count = serializers.IntegerField()
    blur_count = serializers.IntegerField()
    active_ms = serializers.IntegerField()


class DisqualifiedSerializer(serializers.Serializer[Any]):
    username = serializers.CharField()
    reason = serializers.CharField()
    at = serializers.DateTimeField()


class IntegrityReportSerializer(serializers.Serializer[Any]):
    results = IntegrityRowSerializer(many=True)
    disqualified = DisqualifiedSerializer(many=True)


class DisqualifySerializer(serializers.Serializer[Any]):
    username = serializers.CharField(max_length=150)
    reason = serializers.CharField(max_length=2000)
