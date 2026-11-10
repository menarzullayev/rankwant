"""Course studio (ADR-0056, part 4) — `studio/courses/` and `staff/courses/`.

The rules are in `courses.review`: any signed-in user writes up to
`MAX_DRAFTS` unpublished courses; text is editable at any time; structure
and settings only while unpublished (staff-content any time); access and
price are staff's, set at publishing.
"""

from __future__ import annotations

from typing import Any, ClassVar

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from core.permissions import StaffContent
from core.staff import SessionOnly
from courses import hls, review, videos
from courses.author_serializers import (
    CourseReturnSerializer,
    StaffCourseSerializer,
    StudioCourseCreateSerializer,
    StudioCourseSerializer,
    StudioLessonSerializer,
    StudioModuleSerializer,
    StudioSectionSerializer,
    StudioTextSerializer,
    StudioVideoSerializer,
    VideoUploadCompleteSerializer,
    VideoUploadStartedSerializer,
    VideoUploadStartSerializer,
)
from courses.models import (
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


class CourseDraftLimit(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "course_draft_limit"
    default_detail = f"At most {review.MAX_DRAFTS} unpublished courses per author"


class CourseReviewNotReady(APIException):
    """`details.missing` lists stable codes, so the page can say which."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "course_review_not_ready"
    default_detail = "The course is not ready for review"


class CourseStructureLocked(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "course_structure_locked"
    default_detail = "A published course's structure is changed by staff"


class CourseAlreadyPublished(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "course_already_published"
    default_detail = "A published course is not sent for review again"


def tree(queryset: QuerySet[Course]) -> QuerySet[Course]:
    lessons = Lesson.objects.select_related("problem", "quiz").prefetch_related("translations")
    sections = Section.objects.prefetch_related(
        "translations", Prefetch("lessons", queryset=lessons)
    )
    modules = Module.objects.prefetch_related(
        "translations", Prefetch("sections", queryset=sections)
    )
    return queryset.prefetch_related("translations", Prefetch("modules", queryset=modules))


def _user(request: Request) -> User:
    user = request.user
    assert isinstance(user, User)
    return user


def _notify(users: Any, code: str, params: dict[str, Any], ref_type: str, ref_id: str) -> None:
    # Through the service only: `notifications.models` is another app's model.
    from notifications.services import notify_many

    notify_many(users, "system", code=code, params=params, ref_type=ref_type, ref_id=ref_id)


def check_sellable(course: Course) -> None:
    """Price rules (`Course.clean`) and, for a paid course, R2-only video.

    Run whenever staff change access or publish: a free course may hold
    YouTube lessons, and pricing it later must not leave them shareable.
    """
    try:
        course.clean()
    except DjangoValidationError as error:
        raise ValidationError(error.message_dict) from error
    if course.access == Course.Access.PAID:
        shared = Lesson.objects.filter(
            section__module__course=course, kind=Lesson.Kind.VIDEO
        ).exclude(video_provider=Lesson.VideoProvider.HLS)
        if shared.exists():
            raise ValidationError(
                {"access": "Move every video to R2 (HLS) before pricing the course."}
            )


def _title(course: Course) -> str:
    row = next((t for t in course.translations.all() if t.locale == course.base_locale), None)
    return row.title if row else course.slug


@crud_summaries(
    one="kurs qoralamasi",
    many="kurs qoralamalari",
    only=("list", "retrieve", "create", "partial_update", "destroy"),
    extra={"review": "Kursni xodim ko'rigiga yuborish", "text": "Kurs matnini yozish"},
)
class MineCourseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[Course],
):
    serializer_class = StudioCourseSerializer
    permission_classes = [IsAuthenticated, SessionOnly]
    lookup_field = "slug"
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self) -> QuerySet[Course]:  # type: ignore[override]
        if getattr(self, "swagger_fake_view", False):
            return Course.objects.none()
        return tree(review.editable_courses(_user(self.request))).order_by("-pk")

    @extend_schema(request=StudioCourseCreateSerializer, responses={201: StudioCourseSerializer})
    def create(self, request: Request) -> Response:
        user = _user(request)
        data = StudioCourseCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        drafts = Course.objects.filter(authors=user, is_published=False).count()
        if not review.is_course_staff(user) and drafts >= review.MAX_DRAFTS:
            raise CourseDraftLimit()
        with transaction.atomic():
            course = Course.objects.create(
                slug=values["slug"],
                base_locale=values["base_locale"],
                level=values["level"],
                access=Course.Access.FREE,
            )
            course.authors.add(user)
            CourseTranslation.objects.create(
                course=course,
                locale=values["base_locale"],
                title=values["title"],
                summary=values.get("summary", ""),
            )
        course = self.get_queryset().get(pk=course.pk)
        return Response(self.get_serializer(course).data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer: Any) -> None:
        if not review.structure_open(self.request.user, serializer.instance):
            raise CourseStructureLocked()
        serializer.save()

    def perform_destroy(self, instance: Course) -> None:
        if instance.is_published:
            raise CourseStructureLocked()
        instance.delete()

    @extend_schema(request=None, responses={200: StudioCourseSerializer})
    @action(detail=True, methods=["post"])
    def review(self, request: Request, slug: str | None = None) -> Response:
        """Ask staff-content to review. Asking twice tells them once."""
        course = self.get_object()
        if course.is_published:
            raise CourseAlreadyPublished()
        gaps = review.review_gaps(course)
        if gaps:
            raise CourseReviewNotReady(detail={"missing": gaps})
        if course.review_requested_at is None:
            course.review_requested_at = timezone.now()
            course.save(update_fields=["review_requested_at", "updated_at"])
            _notify(
                review.reviewers(),
                "course_review_requested",
                {"course": _title(course), "user": _user(request).username},
                "course_review",
                course.slug,
            )
        return Response(self.get_serializer(self.get_queryset().get(pk=course.pk)).data)

    @extend_schema(request=StudioTextSerializer, responses={200: StudioCourseSerializer})
    @action(detail=True, methods=["post"])
    def text(self, request: Request, slug: str | None = None) -> Response:
        """Write one translation of the course or one of its parts.

        Allowed on a published course too: text goes live at once. Clearing
        every field of a non-base translation removes it.
        """
        course = self.get_object()
        data = StudioTextSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = dict(data.validated_data)
        target = values.pop("target")
        locale = values.pop("locale")
        owner_id = values.pop("id", None)
        model, owner_field, owner, fields = _text_target(course, target, owner_id)
        fields_given = {k: v for k, v in values.items() if k in fields}
        row = model.objects.filter(**{owner_field: owner, "locale": locale}).first()
        if row is None:
            row = model(**{owner_field: owner, "locale": locale})
        for key, value in fields_given.items():
            setattr(row, key, value)
        empty = all(not str(getattr(row, f) or "").strip() for f in fields)
        if empty and locale != course.base_locale:
            if row.pk:
                row.delete()
        else:
            row.save()
        course.save(update_fields=["updated_at"])
        return Response(self.get_serializer(self.get_queryset().get(pk=course.pk)).data)


def _text_target(
    course: Course, target: str, owner_id: int | None
) -> tuple[Any, str, Any, tuple[str, ...]]:
    if target == "course":
        return (
            CourseTranslation,
            "course",
            course,
            ("title", "summary", "description", "outcomes", "requirements", "audience"),
        )
    if owner_id is None:
        raise PermissionDenied("Say which part of the course this text belongs to.")
    if target == "module":
        return (
            ModuleTranslation,
            "module",
            get_object_or_404(Module, pk=owner_id, course=course),
            ("title",),
        )
    if target == "section":
        section = get_object_or_404(Section, pk=owner_id, module__course=course)
        return SectionTranslation, "section", section, ("title",)
    lesson = get_object_or_404(Lesson, pk=owner_id, section__module__course=course)
    return LessonTranslation, "lesson", lesson, ("title", "body")


class _CoursePart(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[Any],
):
    """Modules, sections and lessons of one course in the studio.

    Every write is structure: open to the author while the course is
    unpublished, to staff-content always.
    """

    permission_classes = [IsAuthenticated, SessionOnly]
    http_method_names = ["post", "patch", "delete"]
    course_path: ClassVar[str] = ""

    def course(self) -> Course:
        if not hasattr(self, "_course"):
            courses = review.editable_courses(_user(self.request))
            self._course = get_object_or_404(courses, slug=self.kwargs["course_slug"])
        return self._course

    def check_structure(self) -> None:
        if not review.structure_open(self.request.user, self.course()):
            raise CourseStructureLocked()

    def get_queryset(self) -> Any:
        if getattr(self, "swagger_fake_view", False):
            return self.serializer_class.Meta.model.objects.none()  # type: ignore[union-attr]
        model = self.serializer_class.Meta.model  # type: ignore[union-attr]
        return model.objects.filter(**{self.course_path: self.course()})

    def get_serializer_context(self) -> dict[str, Any]:
        context = dict(super().get_serializer_context())
        if not getattr(self, "swagger_fake_view", False):
            context["course"] = self.course()
        return context

    def perform_create(self, serializer: Any) -> None:
        self.check_structure()
        self.save_new(serializer)

    def save_new(self, serializer: Any) -> None:
        serializer.save()

    def perform_update(self, serializer: Any) -> None:
        self.check_structure()
        serializer.save()

    def perform_destroy(self, instance: Any) -> None:
        self.check_structure()
        instance.delete()


@crud_summaries(
    one="kurs moduli", many="kurs modullari", only=("create", "partial_update", "destroy")
)
class MineModuleViewSet(_CoursePart):
    serializer_class = StudioModuleSerializer
    course_path = "course"

    def save_new(self, serializer: Any) -> None:
        serializer.save(course=self.course())


@crud_summaries(
    one="kurs bo'limi", many="kurs bo'limlari", only=("create", "partial_update", "destroy")
)
class MineSectionViewSet(_CoursePart):
    serializer_class = StudioSectionSerializer
    course_path = "module__course"


@crud_summaries(
    one="kurs darsi", many="kurs darslari", only=("create", "partial_update", "destroy")
)
class MineLessonViewSet(_CoursePart):
    serializer_class = StudioLessonSerializer
    course_path = "section__module__course"


@crud_summaries(
    one="kurs (xodim)",
    many="kurslar (xodim)",
    only=("list", "retrieve", "partial_update"),
    extra={"publish": "Kursni nashr qilish", "send_back": "Kursni muallifga qaytarish"},
)
class StaffCourseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet[Course],
):
    """Staff-content: the review queue (`?review=1`), price and publishing."""

    serializer_class = StaffCourseSerializer
    permission_classes = [StaffContent]
    lookup_field = "slug"
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self) -> QuerySet[Course]:  # type: ignore[override]
        qs = tree(Course.objects.all()).prefetch_related("authors").order_by("-pk")
        if self.request.query_params.get("review") == "1":
            qs = qs.filter(review_requested_at__isnull=False, is_published=False)
        return qs

    @transaction.atomic
    def perform_update(self, serializer: Any) -> None:
        check_sellable(serializer.save())

    @extend_schema(request=None, responses={200: StaffCourseSerializer})
    @action(detail=True, methods=["post"])
    def publish(self, request: Request, slug: str | None = None) -> Response:
        course = self.get_object()
        gaps = review.review_gaps(course)
        if gaps:
            raise CourseReviewNotReady(detail={"missing": gaps})
        check_sellable(course)
        first = not course.is_published
        course.is_published = True
        course.published_at = course.published_at or timezone.now()
        course.review_requested_at = None
        course.save(
            update_fields=["is_published", "published_at", "review_requested_at", "updated_at"]
        )
        if first:
            _notify(
                course.authors.all(),
                "course_published",
                {"course": _title(course)},
                "course",
                course.slug,
            )
        return Response(self.get_serializer(self.get_queryset().get(pk=course.pk)).data)

    @extend_schema(request=CourseReturnSerializer, responses={200: StaffCourseSerializer})
    @action(detail=True, methods=["post"], url_path="send-back")
    def send_back(self, request: Request, slug: str | None = None) -> Response:
        """Return a draft to its authors with the reason."""
        course = self.get_object()
        if course.is_published:
            raise CourseAlreadyPublished()
        data = CourseReturnSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        course.review_requested_at = None
        course.save(update_fields=["review_requested_at", "updated_at"])
        _notify(
            course.authors.all(),
            "course_returned",
            {"course": _title(course), "reason": data.validated_data["reason"]},
            "studio_course",
            course.slug,
        )
        return Response(self.get_serializer(self.get_queryset().get(pk=course.pk)).data)


class VideoUnavailableError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = "course_video_unavailable"
    default_detail = "Course video storage is not configured yet"


class VideoUploadRefused(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "course_video_refused"
    default_detail = "The video upload was refused"


@crud_summaries(
    one="kurs videosi",
    many="kurs videolari",
    only=("list", "destroy"),
    extra={"create": "Video yuklashni boshlash", "complete": "Video yuklashni yakunlash"},
)
class MineVideoViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[VideoAsset],
):
    """A course's own videos (ADR-0056 § 3.5, part 5c).

    The browser uploads the original straight to the bucket in parts (the
    site caps a request at 100 MB); `complete` queues the encoding on the
    video worker. Anyone who may open the course in the studio may upload;
    attaching a video to a lesson follows the structure rules.
    """

    serializer_class = StudioVideoSerializer
    permission_classes = [IsAuthenticated, SessionOnly]
    http_method_names = ["get", "post", "delete"]
    pagination_class = None

    def course(self) -> Course:
        if not hasattr(self, "_course"):
            courses = review.editable_courses(_user(self.request))
            self._course = get_object_or_404(courses, slug=self.kwargs["course_slug"])
        return self._course

    def get_queryset(self) -> QuerySet[VideoAsset]:  # type: ignore[override]
        if getattr(self, "swagger_fake_view", False):
            return VideoAsset.objects.none()
        return VideoAsset.objects.filter(course=self.course()).order_by("-pk")

    def get_serializer_context(self) -> dict[str, Any]:
        context = dict(super().get_serializer_context())
        if not getattr(self, "swagger_fake_view", False):
            context["used_keys"] = set(
                Lesson.objects.filter(
                    section__module__course=self.course(),
                    video_provider=Lesson.VideoProvider.HLS,
                ).values_list("video_ref", flat=True)
            )
        return context

    @extend_schema(
        request=VideoUploadStartSerializer, responses={201: VideoUploadStartedSerializer}
    )
    def create(self, request: Request, course_slug: str | None = None) -> Response:
        if not hls.configured():
            raise VideoUnavailableError()
        data = VideoUploadStartSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        try:
            asset, urls, part = videos.start_upload(
                self.course(),
                _user(request),
                filename=values["filename"],
                size=values["size"],
                heights=values["heights"],
            )
        except videos.UploadRefused as error:
            raise VideoUploadRefused(detail=str(error)) from error
        body = {"video": self.get_serializer(asset).data, "part_size": part, "parts": urls}
        return Response(body, status=status.HTTP_201_CREATED)

    @extend_schema(request=VideoUploadCompleteSerializer, responses={200: StudioVideoSerializer})
    @action(detail=True, methods=["post"])
    def complete(
        self, request: Request, course_slug: str | None = None, pk: str | None = None
    ) -> Response:
        asset = self.get_object()
        data = VideoUploadCompleteSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        try:
            videos.complete_upload(asset, data.validated_data["parts"])
        except videos.UploadRefused as error:
            raise VideoUploadRefused(detail=str(error)) from error
        return Response(self.get_serializer(asset).data)

    def perform_destroy(self, instance: VideoAsset) -> None:
        try:
            videos.discard(instance)
        except videos.UploadRefused as error:
            raise VideoUploadRefused(detail=str(error)) from error
