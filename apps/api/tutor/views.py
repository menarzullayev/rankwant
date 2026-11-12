from __future__ import annotations

from typing import Any

from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from problems import translations, visibility
from tutor import gate, services
from tutor.models import Conversation, Message
from tutor.serializers import TutorAskSerializer, TutorConversationSerializer


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
            conversation.messages.order_by("created_at", "pk")
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
