from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from classroom.models import Assignment, Classroom, ClassroomMember
from courses import teaching
from problems.models import Problem


class ClassroomMemberSerializer(serializers.ModelSerializer[ClassroomMember]):
    username = serializers.CharField(source="user.username", read_only=True)
    rating_skills = serializers.IntegerField(source="user.rating_skills", read_only=True)

    class Meta:
        model = ClassroomMember
        fields = ["username", "role", "rating_skills", "joined_at"]


class ClassroomSerializer(serializers.ModelSerializer[Classroom]):
    owner = serializers.CharField(source="owner.username", read_only=True)
    member_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Classroom
        fields = ["slug", "name", "description", "owner", "member_count", "created_at"]


class ClassroomOwnerSerializer(ClassroomSerializer):
    """Egasi uchun — qo'shilish kodi ko'rinadi."""

    members = ClassroomMemberSerializer(many=True, read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = [*ClassroomSerializer.Meta.fields, "join_code", "is_active", "members"]


class ClassroomCreateSerializer(serializers.ModelSerializer[Classroom]):
    class Meta:
        model = Classroom
        fields = ["slug", "name", "description"]


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
    problems = serializers.ListField(
        child=serializers.SlugField(), required=False, allow_empty=True, default=list
    )
    #: A published course's slug (ADR-0056 part 8).
    course = serializers.SlugField(required=False, allow_blank=True, default="")
    due_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("problems") and not attrs.get("course"):
            raise serializers.ValidationError("Give the class problems, a course or both.")
        return attrs


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
