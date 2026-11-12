from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.http import Http404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import StaffOps
from core.staff import StaffViewSet
from problems import translations, visibility
from tutor import budget, gate, services
from tutor.models import Conversation, Message, Report
from tutor.serializers import (
    StaffTutorReportSerializer,
    TutorAskSerializer,
    TutorBudgetSerializer,
    TutorConversationSerializer,
    TutorReportCreateSerializer,
)


def _error(exc: services.TutorError) -> Response:
    body = {"error": {"code": exc.code, "message": exc.message, "details": exc.details}}
    return Response(body, status=exc.http)


class ProblemTutorView(APIView):
    """The student's tutor conversation on one problem (ADR-0065).

    The problem is looked up like its detail page (`visibility.openable`),
    so a problem the student may not open has no conversation either.
    """

    permission_classes = (IsAuthenticated,)

    def _problem(self, request: Request, slug: str) -> Any:
        problem = visibility.openable(slug, user=request.user)
        if problem is None:
            raise Http404
        return problem

    def _payload(self, request: Request, problem: Any) -> dict[str, Any]:
        conversation = Conversation.objects.filter(user=request.user.pk, problem=problem).first()
        if not services.enabled():
            reason: str | None = "ai_unavailable"
        else:
            reason = gate.closed_reason(problem)
        messages: Any = (
            conversation.messages.prefetch_related("reports").order_by("created_at", "pk")
            if conversation
            else Message.objects.none()
        )
        return TutorConversationSerializer(
            {
                "available": reason is None,
                "reason": reason,
                "hint_level": conversation.hint_level if conversation else 0,
                "usage": services.usage(request.user),
                "messages": messages,
            }
        ).data

    @extend_schema(summary="AI ustoz suhbati", responses={200: TutorConversationSerializer})
    def get(self, request: Request, slug: str) -> Response:
        return Response(self._payload(request, self._problem(request, slug)))

    @extend_schema(
        summary="AI ustozdan so'rash",
        request=TutorAskSerializer,
        responses={
            202: TutorConversationSerializer,
            403: OpenApiResponse(description="ai_off_in_contest"),
            409: OpenApiResponse(description="tutor_busy"),
            429: OpenApiResponse(description="tutor_limit"),
            503: OpenApiResponse(description="ai_unavailable"),
        },
    )
    def post(self, request: Request, slug: str) -> Response:
        problem = self._problem(request, slug)
        body = TutorAskSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data
        try:
            services.ask(
                request.user,
                problem,
                kind=data["kind"],
                locale=translations.reader_locale(request),
                question=data.get("question", ""),
                hint_level=data.get("hint_level"),
                attempt_id=data.get("attempt"),
                code=data.get("code", ""),
                code_language=data.get("code_language", ""),
            )
        except services.TutorError as exc:
            return _error(exc)
        return Response(self._payload(request, problem), status=status.HTTP_202_ACCEPTED)

    @extend_schema(summary="Suhbatni o'chirish", responses={204: None})
    def delete(self, request: Request, slug: str) -> Response:
        problem = self._problem(request, slug)
        Conversation.objects.filter(user=request.user.pk, problem=problem).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProblemTutorReportView(ProblemTutorView):
    """The student flags one of their own tutor replies (decision ⑦)."""

    # Only POST: the parent's GET and DELETE belong to the conversation itself.
    http_method_names = ["post", "options"]

    @extend_schema(
        summary="AI ustoz javobiga shikoyat",
        request=TutorReportCreateSerializer,
        responses={201: None, 404: OpenApiResponse(description="reply_not_found"),
                   409: OpenApiResponse(description="already_reported")},
    )  # fmt: skip
    def post(self, request: Request, slug: str) -> Response:
        problem = self._problem(request, slug)
        body = TutorReportCreateSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        data = body.validated_data
        try:
            services.report(
                request.user,
                problem,
                message_id=data["message"],
                reason=data["reason"],
                note=data.get("note", ""),
            )
        except services.TutorError as exc:
            return _error(exc)
        return Response(status=status.HTTP_201_CREATED)


class StaffTutorReportViewSet(StaffViewSet):
    """Reported tutor replies — the only conversations staff see (decision ⑦).

    Open ones first. Only the status changes; the copied texts are the
    student's report and stay as they were.
    """

    permission_classes = [StaffOps]
    serializer_class = StaffTutorReportSerializer
    queryset = Report.objects.select_related("problem", "user")
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ["status", "reason"]
    search_fields = ["problem__slug", "user__username", "note"]
    ordering_fields = ["created_at", "status", "pk"]
    ordering = ["status", "-created_at", "-pk"]

    def perform_update(self, serializer: Any) -> None:
        closed = serializer.validated_data.get("status", Report.Status.OPEN) != Report.Status.OPEN
        serializer.save(resolved_at=timezone.now() if closed else None)


class StaffTutorBudgetView(APIView):
    """This month's spend against the limit staff set (decision ⑧)."""

    permission_classes = (StaffOps,)

    @extend_schema(summary="AI ustoz oylik byudjeti", responses={200: TutorBudgetSerializer})
    def get(self, request: Request) -> Response:
        return Response(TutorBudgetSerializer(budget.summary()).data)

    @extend_schema(
        summary="AI ustoz oylik chegarasi",
        request=TutorBudgetSerializer,
        responses={200: TutorBudgetSerializer},
    )
    def patch(self, request: Request) -> Response:
        body = TutorBudgetSerializer(data=request.data, partial=True)
        body.is_valid(raise_exception=True)
        if "limit_usd" in body.validated_data:
            budget.set_limit(Decimal(body.validated_data["limit_usd"]))
        return Response(TutorBudgetSerializer(budget.summary()).data)
