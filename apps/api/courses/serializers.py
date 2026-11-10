"""Read-side shapes for the public courses API.

Every text field is picked in the reader's language with the course's base
language as the fallback (`courses.i18n.pick`); `locale` says which one the
reader actually got, so the site can mark a fallback the same way it marks
content names (`ContentName`).
"""

from __future__ import annotations

from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from courses import progress, videos
from courses.access import plan_covers_courses
from courses.i18n import pick
from courses.models import Course, CourseCertificate, Enrollment, Lesson


def _text(obj: Any, locale: str, base: str) -> Any:
    return pick(list(obj.translations.all()), locale, base)


def _value(obj: Any, locale: str, base: str, field: str) -> str:
    """One text field in the reader's language.

    A translation is often partial (the title is done, the description is
    not), so an empty field falls back to the base language and then to any
    translation that has it, instead of leaving the block blank.
    """
    rows = list(obj.translations.all())
    first = pick(rows, locale, base)
    order = ([first] if first else []) + [r for r in rows if r.locale == base] + rows
    for row in order:
        value = getattr(row, field)
        if value:
            return str(value)
    return ""


class ProgressSerializer(serializers.Serializer[progress.CourseState]):
    done = serializers.IntegerField(source="required_done")
    total = serializers.SerializerMethodField()
    percent = serializers.IntegerField()
    completed = serializers.BooleanField(source="is_complete")

    def get_total(self, obj: progress.CourseState) -> int:
        return len(obj.required)


class EnrollmentSerializer(serializers.ModelSerializer[Enrollment]):
    #: The reader's certificate for this course, once issued.
    certificate = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ["source", "created_at", "completed_at", "certificate"]
        read_only_fields = fields

    def get_certificate(self, obj: Enrollment) -> str | None:
        row = CourseCertificate.objects.filter(user_id=obj.user_id, course_id=obj.course_id).first()
        return str(row.pk) if row else None


class EnrollInputSerializer(serializers.Serializer[dict[str, Any]]):
    #: For a Qvant course: the price the reader saw and agreed to.
    confirm_price = serializers.IntegerField(required=False, allow_null=True)


class CourseCertificateSerializer(serializers.ModelSerializer[CourseCertificate]):
    username = serializers.CharField(source="user.username", read_only=True)
    course_slug = serializers.CharField(source="course.slug", read_only=True)

    class Meta:
        model = CourseCertificate
        fields = [
            "id",
            "name",
            "username",
            "course_title",
            "course_slug",
            "final_score",
            "issued_at",
        ]
        read_only_fields = fields


class CourseCardSerializer(serializers.ModelSerializer[Course]):
    title = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    locale = serializers.SerializerMethodField()
    locales = serializers.SerializerMethodField()
    lesson_count = serializers.IntegerField(read_only=True)
    module_count = serializers.IntegerField(read_only=True)
    enrolled = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "slug",
            "title",
            "summary",
            "locale",
            "locales",
            "level",
            "access",
            "price_qvant",
            "price_uzs",
            "cover_url",
            "lesson_count",
            "module_count",
            "published_at",
            "enrolled",
            "percent",
        ]
        read_only_fields = fields

    def _row(self, obj: Course) -> Any:
        return _text(obj, self.context["locale"], obj.base_locale)

    def get_title(self, obj: Course) -> str:
        row = self._row(obj)
        return row.title if row else obj.slug

    def get_summary(self, obj: Course) -> str:
        return _value(obj, self.context["locale"], obj.base_locale, "summary")

    def get_locale(self, obj: Course) -> str:
        row = self._row(obj)
        return row.locale if row else obj.base_locale

    def get_locales(self, obj: Course) -> list[str]:
        return sorted(t.locale for t in obj.translations.all())

    def get_enrolled(self, obj: Course) -> bool:
        return obj.pk in self.context.get("percents", {})

    def get_percent(self, obj: Course) -> int | None:
        percents: dict[int, int] = self.context.get("percents", {})
        return percents.get(obj.pk)


class LessonRowSerializer(serializers.ModelSerializer[Lesson]):
    title = serializers.SerializerMethodField()
    #: The title's language (ADR-0059: Uzbek follows the reader's alphabet).
    locale = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "locale",
            "kind",
            "is_required",
            "is_preview",
            "video_seconds",
            "state",
        ]
        read_only_fields = fields

    def get_title(self, obj: Lesson) -> str:
        row = _text(obj, self.context["locale"], self.context["base"])
        return row.title if row else ""

    def get_locale(self, obj: Lesson) -> str:
        row = _text(obj, self.context["locale"], self.context["base"])
        return str(row.locale if row else self.context["base"])

    def get_state(self, obj: Lesson) -> str:
        """`done`, `open` or `locked` for this reader."""
        state: progress.CourseState = self.context["state"]
        if obj.id in state.completed:
            return "done"
        if state.enrollment is None:
            return "open" if obj.is_preview else "locked"
        return "open" if obj.id in state.unlocked else "locked"


def curriculum(course: Course, context: dict[str, Any]) -> list[dict[str, Any]]:
    locale, base = context["locale"], course.base_locale
    ctx = {**context, "base": base}
    out: list[dict[str, Any]] = []
    for module in course.modules.all():
        row = _text(module, locale, base)
        sections = []
        for section in module.sections.all():
            srow = _text(section, locale, base)
            sections.append(
                {
                    "id": section.id,
                    "title": srow.title if srow else "",
                    "locale": srow.locale if srow else base,
                    "lessons": LessonRowSerializer(
                        section.lessons.all(), many=True, context=ctx
                    ).data,
                }
            )
        out.append(
            {
                "id": module.id,
                "title": row.title if row else "",
                "locale": row.locale if row else base,
                "reward_qvant": module.reward_qvant,
                "sections": sections,
            }
        )
    return out


class SectionOutlineSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    locale = serializers.CharField()
    lessons = LessonRowSerializer(many=True)


class ModuleOutlineSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    locale = serializers.CharField()
    reward_qvant = serializers.IntegerField()
    sections = SectionOutlineSerializer(many=True)


class AuthorSerializer(serializers.Serializer[Any]):
    username = serializers.CharField()
    display_name = serializers.CharField()


class CourseDetailSerializer(CourseCardSerializer):
    description = serializers.SerializerMethodField()
    outcomes = serializers.SerializerMethodField()
    requirements = serializers.SerializerMethodField()
    audience = serializers.SerializerMethodField()
    authors = AuthorSerializer(many=True, read_only=True)
    modules = serializers.SerializerMethodField()
    enrollment = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    has_final_quiz = serializers.SerializerMethodField()
    #: The reader's paid plan opens this paid course (ADR-0057).
    plan_covers = serializers.SerializerMethodField()
    final_quiz_slug: Any = serializers.SlugRelatedField(
        source="final_quiz", slug_field="slug", read_only=True
    )

    class Meta(CourseCardSerializer.Meta):
        fields = [
            *CourseCardSerializer.Meta.fields,
            "description",
            "outcomes",
            "requirements",
            "audience",
            "sequential",
            "certificate_threshold",
            "reward_qvant",
            "has_final_quiz",
            "final_quiz_slug",
            "plan_covers",
            "authors",
            "modules",
            "enrollment",
            "progress",
        ]
        read_only_fields = fields

    def _field(self, obj: Course, name: str) -> str:
        return _value(obj, self.context["locale"], obj.base_locale, name)

    def get_description(self, obj: Course) -> str:
        return self._field(obj, "description")

    def get_outcomes(self, obj: Course) -> str:
        return self._field(obj, "outcomes")

    def get_requirements(self, obj: Course) -> str:
        return self._field(obj, "requirements")

    def get_audience(self, obj: Course) -> str:
        return self._field(obj, "audience")

    def get_has_final_quiz(self, obj: Course) -> bool:
        return obj.final_quiz_id is not None

    def get_plan_covers(self, obj: Course) -> bool:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return obj.access == Course.Access.PAID and plan_covers_courses(user)

    @extend_schema_field(ModuleOutlineSerializer(many=True))
    def get_modules(self, obj: Course) -> list[dict[str, Any]]:
        # Already serialised; `ModuleOutlineSerializer` only describes the shape.
        return curriculum(obj, dict(self.context))

    @extend_schema_field(EnrollmentSerializer(allow_null=True))
    def get_enrollment(self, obj: Course) -> dict[str, Any] | None:
        state: progress.CourseState = self.context["state"]
        if state.enrollment is None:
            return None
        return EnrollmentSerializer(state.enrollment).data  # type: ignore[return-value]

    @extend_schema_field(ProgressSerializer)
    def get_progress(self, obj: Course) -> dict[str, Any]:
        return ProgressSerializer(self.context["state"]).data  # type: ignore[return-value]


class LessonProblemSerializer(serializers.Serializer[Any]):
    slug = serializers.CharField()
    code = serializers.IntegerField(allow_null=True)
    title = serializers.CharField()


class LessonQuizSerializer(serializers.Serializer[Any]):
    slug = serializers.CharField()
    title = serializers.CharField()


class LessonVideoSerializer(serializers.Serializer[dict[str, Any]]):
    provider = serializers.CharField()
    ref = serializers.CharField(allow_null=True)
    seconds = serializers.IntegerField()
    #: API path of the HLS master playlist (our own video), else null.
    playlist = serializers.CharField(allow_null=True)


class NeighbourSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    title = serializers.CharField()
    locale = serializers.CharField()
    state = serializers.CharField()


class LessonDetailSerializer(serializers.ModelSerializer[Lesson]):
    title = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    locale = serializers.SerializerMethodField()
    problem = serializers.SerializerMethodField()
    quiz = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    previous = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "body",
            "locale",
            "kind",
            "is_required",
            "is_preview",
            "quiz_pass_percent",
            "problem",
            "quiz",
            "video",
            "completed",
            "previous",
            "next",
            "progress",
        ]
        read_only_fields = fields

    def _row(self, obj: Lesson) -> Any:
        return _text(obj, self.context["locale"], self.context["base"])

    def get_title(self, obj: Lesson) -> str:
        row = self._row(obj)
        return row.title if row else ""

    def get_body(self, obj: Lesson) -> str:
        return _value(obj, self.context["locale"], self.context["base"], "body")

    def get_locale(self, obj: Lesson) -> str:
        row = self._row(obj)
        return str(row.locale if row else self.context["base"])

    @extend_schema_field(LessonProblemSerializer(allow_null=True))
    def get_problem(self, obj: Lesson) -> dict[str, Any] | None:
        # A problem that is not in the archive (a contest that has not ended)
        # is not linked; the course review makes sure it is public.
        problem = obj.problem
        if problem is None or not problem.is_public:
            return None
        return LessonProblemSerializer(problem).data  # type: ignore[return-value]

    @extend_schema_field(LessonQuizSerializer(allow_null=True))
    def get_quiz(self, obj: Lesson) -> dict[str, Any] | None:
        quiz = obj.quiz
        if quiz is None or not quiz.is_published:
            return None
        return LessonQuizSerializer(quiz).data  # type: ignore[return-value]

    @extend_schema_field(LessonVideoSerializer(allow_null=True))
    def get_video(self, obj: Lesson) -> dict[str, Any] | None:
        if obj.kind != Lesson.Kind.VIDEO:
            return None
        # An R2 key is not a playable address: the signed playlist URL comes
        # with the video pipeline (ADR-0056 § 3.6), never the raw key.
        hls = obj.video_provider == Lesson.VideoProvider.HLS
        ref = None if hls else obj.video_ref
        playlist = None
        if hls and videos.asset_for(obj) is not None:
            course = self.context["course_slug"]
            playlist = f"/courses/{course}/lessons/{obj.id}/hls/master.m3u8"
        return {
            "provider": obj.video_provider,
            "ref": ref,
            "seconds": obj.video_seconds,
            "playlist": playlist,
        }

    def get_completed(self, obj: Lesson) -> bool:
        return obj.id in self.context["state"].completed

    def _neighbour(self, lesson_id: int | None) -> dict[str, Any] | None:
        if lesson_id is None:
            return None
        lesson = self.context["lessons"][lesson_id]
        row = LessonRowSerializer(lesson, context=self.context).data
        return {
            "id": row["id"],
            "title": row["title"],
            "locale": row["locale"],
            "state": row["state"],
        }

    @extend_schema_field(NeighbourSerializer(allow_null=True))
    def get_previous(self, obj: Lesson) -> dict[str, Any] | None:
        return self._neighbour(self.context["state"].neighbours(obj.id)[0])

    @extend_schema_field(NeighbourSerializer(allow_null=True))
    def get_next(self, obj: Lesson) -> dict[str, Any] | None:
        return self._neighbour(self.context["state"].neighbours(obj.id)[1])

    @extend_schema_field(ProgressSerializer)
    def get_progress(self, obj: Lesson) -> dict[str, Any]:
        return ProgressSerializer(self.context["state"]).data  # type: ignore[return-value]


class MyCourseSerializer(serializers.Serializer[dict[str, Any]]):
    course = CourseCardSerializer()
    enrollment = EnrollmentSerializer()
    progress = ProgressSerializer()
