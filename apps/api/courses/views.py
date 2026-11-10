"""Public courses API (ADR-0056, part 2).

The catalogue and the course page (programme included) are open to guests,
like every other listing on the site; lessons need a signed-in reader and an
enrolment, except preview lessons (ADR-0054). Only published courses exist
here; drafts live in the studio (part 4).
"""

from __future__ import annotations

from typing import Any

from django.db.models import Count, Prefetch, QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User
from core.openapi_docs import crud_summaries
from courses import progress, services
from courses.models import (
    CONTENT_LOCALES,
    Course,
    Enrollment,
    Lesson,
    LessonProgress,
    Module,
    Section,
)
from courses.serializers import (
    CourseCardSerializer,
    CourseDetailSerializer,
    EnrollmentSerializer,
    LessonDetailSerializer,
    MyCourseSerializer,
    ProgressSerializer,
)

LANG_PARAM = OpenApiParameter(
    "lang",
    OpenApiTypes.STR,
    enum=list(CONTENT_LOCALES),
    description="Content language; falls back to the course's base language.",
)


def content_locale(request: Request) -> str:
    """`?lang=` if it is a content language, else the request's language."""
    for raw in (request.query_params.get("lang"), getattr(request, "LANGUAGE_CODE", "")):
        code = str(raw or "").split("-")[0].lower()
        if code in CONTENT_LOCALES:
            return code
    return ""


def published() -> QuerySet[Course]:
    return Course.objects.filter(is_published=True)


def percents(user: Any, courses: list[Course]) -> dict[int, int]:
    """Course id -> progress percent for the courses `user` is enrolled in."""
    if not getattr(user, "is_authenticated", False) or not courses:
        return {}
    ids = [c.pk for c in courses]
    enrolled = set(
        Enrollment.objects.filter(user=user, course_id__in=ids).values_list("course_id", flat=True)
    )
    if not enrolled:
        return {}
    required = dict(
        Lesson.objects.filter(section__module__course_id__in=enrolled, is_required=True)
        .values("section__module__course_id")
        .annotate(n=Count("id"))
        .values_list("section__module__course_id", "n")
    )
    done = dict(
        LessonProgress.objects.filter(
            user=user,
            lesson__section__module__course_id__in=enrolled,
            lesson__is_required=True,
        )
        .values("lesson__section__module__course_id")
        .annotate(n=Count("id"))
        .values_list("lesson__section__module__course_id", "n")
    )
    return {
        cid: (round(100 * done.get(cid, 0) / required[cid]) if required.get(cid) else 0)
        for cid in enrolled
    }


@crud_summaries(
    one="kurs",
    many="kurslar",
    only=("list", "retrieve"),
    extra={"enroll": "Kursga yozilish"},
)
@extend_schema(parameters=[LANG_PARAM])
class CourseViewSet(viewsets.ReadOnlyModelViewSet[Course]):
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Course]:  # type: ignore[override]
        qs = (
            published()
            .prefetch_related("translations")
            .annotate(
                lesson_count=Count("modules__sections__lessons", distinct=True),
                module_count=Count("modules", distinct=True),
            )
        )
        if self.action == "list":
            level = self.request.query_params.get("level")
            if level in Course.Level.values:
                qs = qs.filter(level=level)
            access = self.request.query_params.get("access")
            if access in Course.Access.values:
                qs = qs.filter(access=access)
            return qs.order_by("order", "-published_at", "id")
        lessons = Lesson.objects.prefetch_related("translations").order_by("order", "id")
        sections = Section.objects.prefetch_related(
            "translations", Prefetch("lessons", queryset=lessons)
        ).order_by("order", "id")
        modules = Module.objects.prefetch_related(
            "translations", Prefetch("sections", queryset=sections)
        ).order_by("order", "id")
        return qs.prefetch_related(Prefetch("modules", queryset=modules), "authors")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return CourseDetailSerializer if self.action == "retrieve" else CourseCardSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        return {**super().get_serializer_context(), "locale": content_locale(self.request)}

    @extend_schema(
        parameters=[
            OpenApiParameter("level", OpenApiTypes.STR, enum=list(Course.Level.values)),
            OpenApiParameter("access", OpenApiTypes.STR, enum=list(Course.Access.values)),
        ]
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))
        rows = list(page) if page is not None else []
        context = {**self.get_serializer_context(), "percents": percents(request.user, rows)}
        data = CourseCardSerializer(rows, many=True, context=context).data
        return self.get_paginated_response(data)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        course = self.get_object()
        state = progress.state(course, request.user)
        context = {
            **self.get_serializer_context(),
            "state": state,
            "percents": {course.pk: state.percent} if state.enrollment else {},
        }
        return Response(CourseDetailSerializer(course, context=context).data)

    @extend_schema(request=None, responses={201: EnrollmentSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request: Request, slug: str | None = None) -> Response:
        course = get_object_or_404(published(), slug=slug)
        assert isinstance(request.user, User)
        enrollment = services.enroll(request.user, course)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


def _lesson(slug: str, lesson_id: int) -> Lesson:
    return get_object_or_404(
        Lesson.objects.select_related(
            "section__module__course", "problem", "quiz"
        ).prefetch_related("translations"),
        pk=lesson_id,
        section__module__course__slug=slug,
        section__module__course__is_published=True,
    )


class LessonDetailView(APIView):
    """One lesson, in the reader's language. Guests get 401 (ADR-0054)."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Dars",
        parameters=[LANG_PARAM],
        responses={200: LessonDetailSerializer},
    )
    def get(self, request: Request, slug: str, lesson_id: int) -> Response:
        lesson = _lesson(slug, lesson_id)
        course = lesson.section.module.course
        state = progress.state(course, request.user)
        services.check_open(request.user, lesson, state)
        neighbours = [i for i in state.neighbours(lesson.id) if i is not None]
        lessons = {
            row.id: row
            for row in Lesson.objects.filter(pk__in=neighbours).prefetch_related("translations")
        }
        context = {
            "request": request,
            "locale": content_locale(request),
            "base": course.base_locale,
            "course_slug": course.slug,
            "state": state,
            "lessons": lessons,
        }
        return Response(LessonDetailSerializer(lesson, context=context).data)


class LessonCompleteView(APIView):
    """Mark a text or video lesson done; problem and quiz lessons finish on their own."""

    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Darsni tugatish", request=None, responses={200: ProgressSerializer})
    def post(self, request: Request, slug: str, lesson_id: int) -> Response:
        lesson = _lesson(slug, lesson_id)
        assert isinstance(request.user, User)
        state = services.complete(request.user, lesson)
        return Response(ProgressSerializer(state).data)


@extend_schema(summary="Mening kurslarim", parameters=[LANG_PARAM])
class MyCoursesView(generics.ListAPIView[Enrollment]):
    """Courses the reader is enrolled in, most recent first."""

    permission_classes = [IsAuthenticated]
    serializer_class = MyCourseSerializer  # type: ignore[assignment]  # rows are built by hand

    def _user(self) -> User:
        user = self.request.user
        assert isinstance(user, User)
        return user

    def get_queryset(self) -> QuerySet[Enrollment]:  # type: ignore[override]
        if getattr(self, "swagger_fake_view", False):
            return Enrollment.objects.none()
        return (
            Enrollment.objects.filter(user=self._user(), course__is_published=True)
            .select_related("course")
            .order_by("-created_at", "-id")
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        page = self.paginate_queryset(self.get_queryset())
        rows = list(page) if page is not None else []
        ids = [row.course_id for row in rows]
        courses = {
            c.pk: c
            for c in published()
            .filter(pk__in=ids)
            .prefetch_related("translations")
            .annotate(
                lesson_count=Count("modules__sections__lessons", distinct=True),
                module_count=Count("modules", distinct=True),
            )
        }
        locale = content_locale(request)
        out = []
        for row in rows:
            course = courses[row.course_id]
            state = progress.state(course, request.user)
            context = {"request": request, "locale": locale, "percents": {course.pk: state.percent}}
            out.append(
                {
                    "course": CourseCardSerializer(course, context=context).data,
                    "enrollment": EnrollmentSerializer(row).data,
                    "progress": ProgressSerializer(state).data,
                }
            )
        return self.get_paginated_response(out)
