from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from classroom import services
from classroom.models import Assignment, Classroom, ClassroomJoinRequest, ClassroomMember
from classroom.serializers import (
    AssignmentCreateSerializer,
    AssignmentSerializer,
    ClassCourseReportSerializer,
    ClassQuizReportSerializer,
    ClassroomCreateSerializer,
    ClassroomManagerSerializer,
    ClassroomOwnerSerializer,
    ClassroomSerializer,
    InviteSerializer,
    JoinRequestSerializer,
    JoinResultSerializer,
    JoinSerializer,
    MemberRoleSerializer,
)
from classroom.services import ClassroomError, assignment_progress, join
from core import quotas
from core.models import User
from core.openapi_docs import crud_summaries
from courses import teaching
from courses.views import content_locale
from problems.models import Problem


def _not_owner(message: str) -> Response:
    return Response(
        {"error": {"code": "not_owner", "message": message, "details": {}}},
        status=status.HTTP_403_FORBIDDEN,
    )


def _failed(exc: ClassroomError) -> Response:
    return Response(
        {"error": {"code": exc.code, "message": str(exc), "details": {}}},
        status=status.HTTP_400_BAD_REQUEST,
    )


@crud_summaries(
    one="sinf",
    many="sinflar",
    extra={
        "join": "Kod bilan sinfga qo'shilish",
        "invite": "Taklif havolasi: sinf haqida qisqa ma'lumot",
        "requests": "Qo'shilish so'rovlari navbati",
        "approve": "So'rovni qabul qilish",
        "reject": "So'rovni rad etish",
        "member": "A'zoning rolini o'zgartirish yoki chiqarish",
        "leave": "Sinfdan chiqish",
        "refresh_code": "Qo'shilish kodini yangilash",
        "assignments": "Topshiriqlar",
        "progress": "O'quvchi progressi",
        "course_report": "Sinfga berilgan kurs: o'quvchilar progressi",
    },
)
class ClassroomViewSet(viewsets.ModelViewSet[Classroom]):
    """PRD P2-2 — o'qituvchi sinfi."""

    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete"]

    #: O'zgartirish va o'chirish FAQAT egasiga. `get_queryset` a'zolarni ham
    #: qaytaradi (ular sinfni ko'rishi kerak), shuning uchun ruxsat alohida
    #: tekshirilmasa o'quvchi o'qituvchining sinfini o'chira olardi.
    OWNER_ONLY_ACTIONS = frozenset({"update", "partial_update", "destroy"})

    def get_queryset(self):  # type: ignore[no-untyped-def]
        # Sxema generatsiyasida `request.user` — AnonymousUser, ya'ni
        # quyidagi `assert` yiqilardi va drf-spectacular modelni topa
        # olmasdan ogohlantirardi (o'lchandi 2026-09-24).
        if getattr(self, "swagger_fake_view", False):
            return Classroom.objects.none()
        assert isinstance(self.request.user, User)
        base = Classroom.objects.filter(is_active=True)
        if self.action in self.OWNER_ONLY_ACTIONS:
            base = base.filter(owner=self.request.user)
        else:
            # To read: the owner OR a member. A subquery, not `members__user`:
            # that join would be shared with the count below, and a member
            # would count only their own row (an assistant saw "0 students").
            mine = ClassroomMember.objects.filter(user=self.request.user).values("classroom")
            base = base.filter(Q(owner=self.request.user) | Q(pk__in=mine))
        return (
            # Students only: assistants are staff of the class, not seats in it.
            base.annotate(
                member_count=Count(
                    "members",
                    filter=Q(members__role=ClassroomMember.Role.STUDENT),
                    distinct=True,
                )
            )
            .select_related("owner")
            .distinct()
        )

    def _is_owner(self) -> bool:
        obj = getattr(self, "_cached_object", None)
        if obj is None:
            return False
        return bool(obj.owner_id == self.request.user.pk)

    def get_object(self) -> Classroom:
        obj = super().get_object()
        self._cached_object = obj
        return obj

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return ClassroomCreateSerializer
        if self.action == "retrieve":
            # The join code goes to the owner ONLY: anyone with it can join.
            # The member list shows classmates' ratings, so it goes to the
            # owner and assistants.
            if self._is_owner():
                return ClassroomOwnerSerializer
            obj = getattr(self, "_cached_object", None)
            user = self.request.user
            # Schema generation has no user and no object: the plain shape.
            if obj is not None and isinstance(user, User) and services.manages(obj, user):
                return ClassroomManagerSerializer
            return ClassroomSerializer
        return ClassroomSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        return Response(self.get_serializer(instance).data)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(request.user, User)
        try:
            # Archived classrooms do not count (`classroom/quotas.py`).
            quotas.enforce(request.user, "classrooms")
        except quotas.QuotaExceeded as exc:
            return Response(exc.as_error(), status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer: Any) -> None:
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance: Classroom) -> None:
        # Archived, not deleted: assignments and reports stay (ADR-0061 § 3).
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    def _context(self) -> dict[str, Any]:
        return {"request": self.request}

    @extend_schema(
        request=JoinSerializer, responses={201: JoinResultSerializer, 202: JoinResultSerializer}
    )
    @action(detail=False, methods=["post"])
    def join(self, request: Request) -> Response:
        serializer = JoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        try:
            result = join(request.user, serializer.validated_data["join_code"])
        except ClassroomError as exc:
            return _failed(exc)
        pending = isinstance(result, ClassroomJoinRequest)
        body = {
            **ClassroomSerializer(result.classroom, context=self._context()).data,
            "status": "pending" if pending else "member",
        }
        return Response(
            body, status=status.HTTP_202_ACCEPTED if pending else status.HTTP_201_CREATED
        )

    @extend_schema(responses={200: InviteSerializer})
    @action(detail=False, methods=["get"], url_path=r"invite/(?P<code>[A-Za-z0-9_-]+)")
    def invite(self, request: Request, code: str = "") -> Response:
        """An invite link's page: whose classroom it is before joining."""
        classroom = get_object_or_404(
            Classroom.objects.select_related("owner"), join_code=code, is_active=True
        )
        assert isinstance(request.user, User)
        role = services.role_of(classroom, request.user)
        pending = classroom.requests.filter(
            user=request.user, status=ClassroomJoinRequest.Status.PENDING
        ).exists()
        state = (
            "owner" if role == "owner" else ("member" if role else ("pending" if pending else ""))
        )
        return Response(
            InviteSerializer(
                {
                    "slug": classroom.slug,
                    "name": classroom.name,
                    "owner": classroom.owner.username,
                    "join_mode": classroom.join_mode,
                    "member_count": services.students(classroom),
                    "state": state,
                }
            ).data
        )

    def _managed(self) -> Classroom | Response:
        classroom = self.get_object()
        assert isinstance(self.request.user, User)
        if not services.manages(classroom, self.request.user):
            return _not_owner("Only the owner or an assistant manages requests")
        return classroom

    @extend_schema(responses={200: JoinRequestSerializer(many=True)})
    @action(detail=True, methods=["get"])
    def requests(self, request: Request, slug: str | None = None) -> Response:
        classroom = self._managed()
        if isinstance(classroom, Response):
            return classroom
        rows = classroom.requests.filter(status=ClassroomJoinRequest.Status.PENDING).select_related(
            "user"
        )
        return Response(JoinRequestSerializer(rows, many=True).data)

    def _decide(self, request: Request, pk: str | None, *, approve: bool) -> Response:
        classroom = self._managed()
        if isinstance(classroom, Response):
            return classroom
        if not classroom.requests.filter(pk=int(pk or 0)).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        assert isinstance(request.user, User)
        try:
            row = services.decide(request.user, int(pk or 0), approve=approve)
        except ClassroomError as exc:
            return _failed(exc)
        return Response(JoinRequestSerializer(row).data)

    @extend_schema(request=None, responses={200: JoinRequestSerializer})
    @action(detail=True, methods=["post"], url_path=r"requests/(?P<pk>\d+)/approve")
    def approve(self, request: Request, slug: str | None = None, pk: str | None = None) -> Response:
        return self._decide(request, pk, approve=True)

    @extend_schema(request=None, responses={200: JoinRequestSerializer})
    @action(detail=True, methods=["post"], url_path=r"requests/(?P<pk>\d+)/reject")
    def reject(self, request: Request, slug: str | None = None, pk: str | None = None) -> Response:
        return self._decide(request, pk, approve=False)

    @extend_schema(request=MemberRoleSerializer, responses={200: None, 204: None})
    @action(detail=True, methods=["patch", "delete"], url_path=r"members/(?P<username>[^/]+)")
    def member(
        self, request: Request, slug: str | None = None, username: str | None = None
    ) -> Response:
        """The owner makes a member an assistant (or a student again) or takes them out."""
        classroom = self.get_object()
        if classroom.owner_id != request.user.pk:
            return _not_owner("Only the classroom owner manages members")
        try:
            if request.method == "DELETE":
                services.remove(classroom, username or "")
                return Response(status=status.HTTP_204_NO_CONTENT)
            serializer = MemberRoleSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            services.set_role(classroom, username or "", serializer.validated_data["role"])
        except ClassroomError as exc:
            return _failed(exc)
        return Response({"username": username, "role": serializer.validated_data["role"]})

    @extend_schema(request=None, responses={204: None})
    @action(detail=True, methods=["post"])
    def leave(self, request: Request, slug: str | None = None) -> Response:
        classroom = self.get_object()
        assert isinstance(request.user, User)
        try:
            services.leave(classroom, request.user)
        except ClassroomError as exc:
            return _failed(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=["post"], url_path="refresh-code")
    def refresh_code(self, request: Request, slug: str | None = None) -> Response:
        classroom = self.get_object()
        if classroom.owner_id != request.user.pk:
            return _not_owner("Only the classroom owner can change the code")
        try:
            code = services.refresh_code(classroom)
        except ClassroomError as exc:
            return _failed(exc)
        return Response({"join_code": code})

    @extend_schema(
        request=AssignmentCreateSerializer,
        responses={200: AssignmentSerializer(many=True), 201: AssignmentSerializer},
    )
    @action(detail=True, methods=["get", "post"])
    def assignments(self, request: Request, slug: str | None = None) -> Response:
        classroom = self.get_object()
        context = {"locale": content_locale(request)}

        if request.method == "GET":
            rows = classroom.assignments.select_related("course", "quiz").prefetch_related(
                "problems", "course__translations"
            )
            return Response(AssignmentSerializer(rows, many=True, context=context).data)

        if classroom.owner_id != request.user.pk:
            return _not_owner("Only the classroom owner can assign work")
        serializer = AssignmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quiz = None
        if data["quiz"]:
            from quizzes.services import assignable

            quiz = assignable(request.user, data["quiz"])
            if quiz is None:
                return Response(
                    {
                        "error": {
                            "code": "classroom_quiz_unavailable",
                            "message": "No quiz of yours or public quiz has this slug.",
                            "details": {},
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        course = None
        if data["course"]:
            course = teaching.assignable(data["course"])
            if course is None:
                return Response(
                    {
                        "error": {
                            "code": "classroom_course_unavailable",
                            "message": "No published course has this slug.",
                            "details": {},
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        with transaction.atomic():
            assignment = Assignment.objects.create(
                classroom=classroom,
                title=data["title"],
                description=data.get("description", ""),
                course=course,
                quiz=quiz,
                due_at=data.get("due_at"),
            )
            assignment.problems.set(Problem.objects.filter(slug__in=data["problems"]))
            if course is not None:
                # A free course opens for every student now; a priced one
                # is unlocked by each student (owner decision 2026-11-10).
                students = classroom.members.filter(
                    role=ClassroomMember.Role.STUDENT
                ).select_related("user")
                teaching.enroll_members(course, [m.user for m in students])
        return Response(
            AssignmentSerializer(assignment, context=context).data, status=status.HTTP_201_CREATED
        )

    @extend_schema(responses={200: ClassCourseReportSerializer})
    @action(detail=True, methods=["get"], url_path=r"assignments/(?P<pk>\d+)/course")
    def course_report(
        self, request: Request, slug: str | None = None, pk: str | None = None
    ) -> Response:
        """Each student's standing in the course given to the class."""
        classroom = self.get_object()
        if classroom.owner_id != request.user.pk:
            return _not_owner("Only the classroom owner can see progress")
        assignment = get_object_or_404(
            classroom.assignments.select_related("course").exclude(course=None), pk=int(pk or 0)
        )
        assert assignment.course is not None
        students = classroom.members.filter(role=ClassroomMember.Role.STUDENT).select_related(
            "user"
        )
        data = teaching.report(
            assignment.course, [m.user for m in students], content_locale(request)
        )
        return Response(ClassCourseReportSerializer(data).data)

    @extend_schema(responses={200: ClassQuizReportSerializer})
    @action(detail=True, methods=["get"], url_path=r"assignments/(?P<pk>\d+)/quiz")
    def quiz_report(
        self, request: Request, slug: str | None = None, pk: str | None = None
    ) -> Response:
        """Each student's best result and the questions most got wrong."""
        classroom = self.get_object()
        if classroom.owner_id != request.user.pk:
            return _not_owner("Only the classroom owner can see results")
        assignment = get_object_or_404(
            classroom.assignments.select_related("quiz").exclude(quiz=None), pk=int(pk or 0)
        )
        assert assignment.quiz is not None
        from quizzes.services import class_report

        students = classroom.members.filter(role=ClassroomMember.Role.STUDENT).select_related(
            "user"
        )
        data = class_report(assignment.quiz, [m.user for m in students])
        return Response(ClassQuizReportSerializer(data).data)

    @extend_schema(responses={200: None})
    @action(detail=True, methods=["get"], url_path=r"assignments/(?P<pk>\d+)/progress")
    def progress(
        self, request: Request, slug: str | None = None, pk: str | None = None
    ) -> Response:
        classroom = self.get_object()
        if classroom.owner_id != request.user.pk:
            return _not_owner("Only the classroom owner can see progress")
        # A missing assignment is a 404, not an unhandled DoesNotExist (500).
        assignment = get_object_or_404(classroom.assignments, pk=int(pk or 0))
        return Response({"results": assignment_progress(assignment)})
