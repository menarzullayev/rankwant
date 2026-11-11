from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from classroom.models import Assignment, Classroom, ClassroomJoinRequest, ClassroomMember
from courses import teaching
from problems.models import Problem


class ClassroomMemberSerializer(serializers.ModelSerializer[ClassroomMember]):
    username = serializers.CharField(source="user.username", read_only=True)
    rating_skills = serializers.IntegerField(source="user.rating_skills", read_only=True)

    class Meta:
        model = ClassroomMember
        fields = ["username", "role", "rating_skills", "joined_at"]


#: Paths under `/classroom/` that a classroom slug must not take.
RESERVED_SLUGS = frozenset({"join"})


def _free_slug(value: str) -> str:
    if value in RESERVED_SLUGS:
        raise serializers.ValidationError("This address is reserved")
    return value


class ClassroomSerializer(serializers.ModelSerializer[Classroom]):
    owner = serializers.CharField(source="owner.username", read_only=True)
    member_count = serializers.IntegerField(read_only=True, default=0)
    #: `owner`, `assistant` or `student` (ADR-0061 § 3): the page shows what
    #: this reader may do from it, not from which fields came back.
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = [
            "slug",
            "name",
            "description",
            "owner",
            "member_count",
            "created_at",
            "join_mode",
            "my_role",
        ]

    def get_my_role(self, obj: Classroom) -> str:
        from classroom.services import role_of

        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return ""
        return role_of(obj, user)

    def validate_slug(self, value: str) -> str:
        return _free_slug(value)


class ClassroomManagerSerializer(ClassroomSerializer):
    """The owner's and an assistant's view: the members and the pending requests."""

    members = ClassroomMemberSerializer(many=True, read_only=True)
    pending_count = serializers.SerializerMethodField()

    class Meta(ClassroomSerializer.Meta):
        fields = [*ClassroomSerializer.Meta.fields, "members", "pending_count"]

    def get_pending_count(self, obj: Classroom) -> int:
        return obj.requests.filter(status=ClassroomJoinRequest.Status.PENDING).count()


class ClassroomOwnerSerializer(ClassroomManagerSerializer):
    """Egasi uchun — qo'shilish kodi ko'rinadi."""

    class Meta(ClassroomManagerSerializer.Meta):
        fields = [*ClassroomManagerSerializer.Meta.fields, "join_code", "is_active"]


class JoinRequestSerializer(serializers.ModelSerializer[ClassroomJoinRequest]):
    username = serializers.CharField(source="user.username", read_only=True)
    rating_skills = serializers.IntegerField(source="user.rating_skills", read_only=True)

    class Meta:
        model = ClassroomJoinRequest
        fields = ["id", "username", "rating_skills", "status", "created_at"]


class JoinResultSerializer(ClassroomSerializer):
    """The classroom, as before, plus `status`: `member` — in it now (201);
    `pending` — waiting for the teacher (202). `/api/v1/` only grows."""

    status = serializers.CharField(read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = [*ClassroomSerializer.Meta.fields, "status"]


class InviteSerializer(serializers.Serializer[dict[str, Any]]):
    """What an invite link shows before joining.

    The slug is no secret here: whoever holds the code may join anyway.
    """

    slug = serializers.CharField()
    name = serializers.CharField()
    owner = serializers.CharField()
    join_mode = serializers.CharField()
    member_count = serializers.IntegerField()
    #: `member`, `pending`, `owner` or `""`.
    state = serializers.CharField()


class MemberRoleSerializer(serializers.Serializer[dict[str, Any]]):
    role = serializers.ChoiceField(choices=ClassroomMember.Role.choices)


class ClassroomCreateSerializer(serializers.ModelSerializer[Classroom]):
    class Meta:
        model = Classroom
        fields = ["slug", "name", "description", "join_mode"]
        extra_kwargs: ClassVar[dict[str, dict[str, Any]]] = {"join_mode": {"required": False}}

    def validate_slug(self, value: str) -> str:
        return _free_slug(value)


class JoinSerializer(serializers.Serializer[dict[str, Any]]):
    join_code = serializers.CharField(max_length=12)


class AssignmentCourseSerializer(serializers.Serializer[dict[str, Any]]):
    slug = serializers.CharField()
    title = serializers.CharField()
    #: The title's language (ADR-0059).
    locale = serializers.CharField()
    #: free / qvant / paid — only a free course enrols the class.
    access = serializers.CharField()
    price_qvant = serializers.IntegerField()


class AssignmentSerializer(serializers.ModelSerializer[Assignment]):
    problems = serializers.SlugRelatedField[Problem](many=True, read_only=True, slug_field="slug")
    course = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ["id", "title", "description", "problems", "course", "due_at", "created_at"]

    @extend_schema_field(AssignmentCourseSerializer(allow_null=True))
    def get_course(self, obj: Assignment) -> dict[str, Any] | None:
        if obj.course is None:
            return None
        return teaching.brief(obj.course, self.context.get("locale", ""))


class AssignmentCreateSerializer(serializers.Serializer[dict[str, Any]]):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    #: Problem slugs or archive numbers (`123` or `#123`).
    problems = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False, allow_empty=True, default=list
    )
    #: A published course's slug (ADR-0056 part 8).
    course = serializers.SlugField(required=False, allow_blank=True, default="")
    due_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("problems") and not attrs.get("course"):
            raise serializers.ValidationError("Give the class problems, a course or both.")
        attrs["problems"] = self._resolve(attrs.get("problems") or [])
        return attrs

    @staticmethod
    def _resolve(given: list[str]) -> list[str]:
        """Slugs or archive numbers (`123`, `#123`) → slugs of public problems.

        An unknown or unpublished one is refused by name: a class would
        otherwise get an assignment with a problem its students cannot open.
        """
        slugs: list[str] = []
        missing: list[str] = []
        for item in given:
            key = item.strip().lstrip("#")
            query = (
                Problem.objects.filter(code=int(key))
                if key.isdigit()
                else Problem.objects.filter(slug=key)
            )
            slug = query.filter(is_public=True).values_list("slug", flat=True).first()
            if slug is None:
                missing.append(item)
            elif slug not in slugs:
                slugs.append(slug)
        if missing:
            # Each one by name, as written: the page lists what was not found.
            raise serializers.ValidationError({"problems": missing})
        return slugs


class ClassCourseLessonSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    kind = serializers.CharField()
    is_required = serializers.BooleanField()


class ClassCourseModuleSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    lessons = ClassCourseLessonSerializer(many=True)


class ClassCourseStudentSerializer(serializers.Serializer[dict[str, Any]]):
    username = serializers.CharField()
    display_name = serializers.CharField()
    enrolled = serializers.BooleanField()
    #: Required lessons done / required lessons, as on the course page.
    done = serializers.IntegerField()
    total = serializers.IntegerField()
    percent = serializers.IntegerField()
    completed_at = serializers.DateTimeField(allow_null=True)
    final_score = serializers.IntegerField(allow_null=True)
    certificate = serializers.CharField(allow_null=True)
    last_activity = serializers.DateTimeField(allow_null=True)
    #: Every lesson done, required or not, in curriculum order.
    lessons = serializers.ListField(child=serializers.IntegerField())


class ClassCourseReportSerializer(serializers.Serializer[dict[str, Any]]):
    course = AssignmentCourseSerializer()
    has_final_quiz = serializers.BooleanField()
    certificate_threshold = serializers.IntegerField()
    modules = ClassCourseModuleSerializer(many=True)
    students = ClassCourseStudentSerializer(many=True)
