"""Studio shapes: the editor reads the whole tree with every translation."""

from __future__ import annotations

from typing import Any

from django.utils.text import slugify
from rest_framework import serializers

from courses import review, video
from courses.models import (
    CONTENT_LOCALES,
    Course,
    CourseTranslation,
    Lesson,
    LessonTranslation,
    Module,
    ModuleTranslation,
    Section,
    SectionTranslation,
    VideoAsset,
)

# Other apps' models are not imported here (`tools/check_architecture.py`):
# the lesson's own foreign keys know them.
_PROBLEMS: Any = Lesson._meta.get_field("problem").related_model
_QUIZZES: Any = Lesson._meta.get_field("quiz").related_model


class CourseTextSerializer(serializers.ModelSerializer[CourseTranslation]):
    class Meta:
        model = CourseTranslation
        fields = [
            "locale",
            "title",
            "summary",
            "description",
            "outcomes",
            "requirements",
            "audience",
        ]


class ModuleTextSerializer(serializers.ModelSerializer[ModuleTranslation]):
    class Meta:
        model = ModuleTranslation
        fields = ["locale", "title"]


class SectionTextSerializer(serializers.ModelSerializer[SectionTranslation]):
    class Meta:
        model = SectionTranslation
        fields = ["locale", "title"]


class LessonTextSerializer(serializers.ModelSerializer[LessonTranslation]):
    class Meta:
        model = LessonTranslation
        fields = ["locale", "title", "body"]


class StudioLessonSerializer(serializers.ModelSerializer[Lesson]):
    """A lesson's structure. Completeness (a problem lesson has a problem…)
    is the review's job, so a half-built lesson can be saved."""

    texts = LessonTextSerializer(source="translations", many=True, read_only=True)
    problem = serializers.SlugRelatedField(
        slug_field="slug", queryset=_PROBLEMS.objects.all(), allow_null=True, required=False
    )
    quiz = serializers.SlugRelatedField(
        slug_field="slug", queryset=_QUIZZES.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Lesson
        fields = [
            "id",
            "section",
            "order",
            "kind",
            "is_required",
            "is_preview",
            "problem",
            "quiz",
            "quiz_pass_percent",
            "video_provider",
            "video_ref",
            "video_seconds",
            "texts",
        ]
        read_only_fields = ["id"]

    def validate_section(self, value: Section) -> Section:
        if value.module.course_id != self.context["course"].pk:
            raise serializers.ValidationError("The section belongs to another course.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        course: Course = self.context["course"]
        kind = attrs.get("kind", getattr(self.instance, "kind", Lesson.Kind.TEXT))
        provider = attrs.get("video_provider", getattr(self.instance, "video_provider", ""))
        preview = attrs.get("is_preview", getattr(self.instance, "is_preview", False))
        if "video_ref" in attrs or "video_provider" in attrs:
            ref = attrs.get("video_ref", getattr(self.instance, "video_ref", ""))
            if provider == Lesson.VideoProvider.HLS and "video_ref" in attrs and ref:
                # An R2 key names a stored video: only this course's own may
                # be attached, or a lesson could point at another course's
                # paid video (and hand out its key).
                own = VideoAsset.objects.filter(
                    key=ref, course=self.context["course"], status=VideoAsset.Status.READY
                ).exists()
                if not own:
                    raise serializers.ValidationError(
                        {"video_ref": "Attach a video uploaded to this course."}
                    )
            if provider and ref:
                try:
                    attrs["video_ref"] = video.normalise(provider, ref)
                except ValueError as error:
                    raise serializers.ValidationError({"video_ref": str(error)}) from error
        if course.access == Course.Access.PAID and kind == Lesson.Kind.VIDEO:
            # ADR-0056 § 3.5: a YouTube or Vimeo link of a paid lesson can be
            # passed around; R2 serves it behind a signed URL.
            if provider and provider != Lesson.VideoProvider.HLS:
                raise serializers.ValidationError(
                    {"video_provider": "Paid courses serve video only from R2 (HLS)."}
                )
            if preview:
                raise serializers.ValidationError(
                    {"is_preview": "A paid course's video is never a preview."}
                )
        return attrs


class StudioSectionSerializer(serializers.ModelSerializer[Section]):
    texts = SectionTextSerializer(source="translations", many=True, read_only=True)
    lessons = StudioLessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "module", "order", "texts", "lessons"]
        read_only_fields = ["id"]

    def validate_module(self, value: Module) -> Module:
        if value.course_id != self.context["course"].pk:
            raise serializers.ValidationError("The module belongs to another course.")
        return value


class StudioModuleSerializer(serializers.ModelSerializer[Module]):
    texts = ModuleTextSerializer(source="translations", many=True, read_only=True)
    sections = StudioSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "order", "reward_qvant", "texts", "sections"]
        read_only_fields = ["id"]

    def validate_reward_qvant(self, value: int) -> int:
        # Qvant is money-like (ADR-0002): only staff set a reward.
        if value and not review.is_course_staff(self.context["request"].user):
            raise serializers.ValidationError("Only staff set a Qvant reward.")
        return value


class StudioCourseSerializer(serializers.ModelSerializer[Course]):
    """The studio's course: settings, texts, tree and review state."""

    texts = CourseTextSerializer(source="translations", many=True, read_only=True)
    modules = StudioModuleSerializer(many=True, read_only=True)
    final_quiz = serializers.SlugRelatedField(
        slug_field="slug", queryset=_QUIZZES.objects.all(), allow_null=True, required=False
    )
    status = serializers.SerializerMethodField()
    gaps = serializers.SerializerMethodField()
    structure_open = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "slug",
            "base_locale",
            "level",
            "sequential",
            "certificate_threshold",
            "final_quiz",
            "cover_url",
            "access",
            "price_qvant",
            "price_uzs",
            "reward_qvant",
            "is_published",
            "published_at",
            "review_requested_at",
            "status",
            "gaps",
            "structure_open",
            "texts",
            "modules",
        ]
        read_only_fields = [
            "slug",
            "access",
            "price_qvant",
            "price_uzs",
            "reward_qvant",
            "is_published",
            "published_at",
            "review_requested_at",
        ]

    def get_status(self, obj: Course) -> str:
        """`published`, `review` or `draft`."""
        if obj.is_published:
            return "published"
        return "review" if obj.review_requested_at else "draft"

    def get_gaps(self, obj: Course) -> list[str]:
        return review.review_gaps(obj)

    def get_structure_open(self, obj: Course) -> bool:
        return review.structure_open(self.context["request"].user, obj)


class StudioCourseCreateSerializer(serializers.Serializer[dict[str, Any]]):
    title = serializers.CharField(max_length=200)
    summary = serializers.CharField(max_length=300, required=False, allow_blank=True)
    slug = serializers.SlugField(max_length=100, required=False, allow_blank=True)
    base_locale = serializers.ChoiceField(choices=list(CONTENT_LOCALES), default="uz")
    level = serializers.ChoiceField(choices=Course.Level.choices, default=Course.Level.BEGINNER)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        slug = attrs.get("slug") or slugify(attrs["title"])[:100]
        if not slug:
            raise serializers.ValidationError(
                {"slug": "Give the course an address in Latin letters."}
            )
        if Course.objects.filter(slug=slug).exists():
            raise serializers.ValidationError({"slug": "This address is taken."})
        attrs["slug"] = slug
        return attrs


class StudioTextSerializer(serializers.Serializer[dict[str, Any]]):
    """One translation of one part of the course."""

    target = serializers.ChoiceField(choices=["course", "module", "section", "lesson"])
    id = serializers.IntegerField(required=False)
    locale = serializers.ChoiceField(choices=list(CONTENT_LOCALES))
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    summary = serializers.CharField(max_length=300, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    outcomes = serializers.CharField(required=False, allow_blank=True)
    requirements = serializers.CharField(required=False, allow_blank=True)
    audience = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)


class StaffCourseSerializer(StudioCourseSerializer):
    """Staff set what authors may not: access, price and the course reward."""

    authors: Any = serializers.SlugRelatedField(slug_field="username", many=True, read_only=True)

    class Meta(StudioCourseSerializer.Meta):
        fields = [*StudioCourseSerializer.Meta.fields, "authors", "order"]
        read_only_fields = [
            "slug",
            "is_published",
            "published_at",
            "review_requested_at",
        ]


class CourseReturnSerializer(serializers.Serializer[dict[str, Any]]):
    reason = serializers.CharField(max_length=1000)


class StudioVideoSerializer(serializers.ModelSerializer[VideoAsset]):
    """A course's uploaded video as the studio lists it (never its AES key)."""

    used = serializers.SerializerMethodField()
    heights = serializers.ListField(child=serializers.IntegerField(), read_only=True)
    requested_heights = serializers.ListField(child=serializers.IntegerField(), read_only=True)

    class Meta:
        model = VideoAsset
        fields = [
            "id",
            "key",
            "status",
            "source",
            "heights",
            "requested_heights",
            "seconds",
            "size",
            "error",
            "created_at",
            "used",
        ]
        read_only_fields = fields

    def get_used(self, obj: VideoAsset) -> bool:
        return obj.key in self.context.get("used_keys", set())


class VideoUploadStartSerializer(serializers.Serializer[dict[str, Any]]):
    filename = serializers.CharField(max_length=255)
    size = serializers.IntegerField(min_value=1)
    heights = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)


class VideoUploadStartedSerializer(serializers.Serializer[dict[str, Any]]):
    video = StudioVideoSerializer()
    part_size = serializers.IntegerField()
    parts = serializers.ListField(child=serializers.URLField())


class VideoPartSerializer(serializers.Serializer[dict[str, Any]]):
    number = serializers.IntegerField(min_value=1, max_value=10_000)
    etag = serializers.CharField(max_length=200)


class VideoUploadCompleteSerializer(serializers.Serializer[dict[str, Any]]):
    parts = VideoPartSerializer(many=True)
