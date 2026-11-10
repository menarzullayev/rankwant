"""Reading and writing a problem's translations (ADR-0058).

One mixin for the author's studio and the staff panel: the viewset decides
who may write (`_check_translation_write`), the rest is the same.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response

from problems import translations
from problems.models import Problem, ProblemTranslation
from problems.serializers import ProblemTranslationSerializer


class TranslationIsBase(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "problem_translation_is_base"
    default_detail = "This is the problem's own language; edit the statement instead."


class TranslationActions:
    """`translations/` (list) and `translations/<locale>/` (put, delete)."""

    if TYPE_CHECKING:  # provided by the viewset; a runtime stub would shadow it

        def get_object(self) -> Problem: ...

    def _check_translation_write(self, problem: Problem) -> None:
        """Raise when this user may not change the problem's text."""

    @extend_schema(request=None, responses={200: ProblemTranslationSerializer(many=True)})
    @action(detail=True, methods=["get"], url_path="translations")
    def translations(self, request: Request, slug: str | None = None) -> Response:
        """Every other language of the problem's text."""
        problem = self.get_object()
        return Response(ProblemTranslationSerializer(problem.translations.all(), many=True).data)

    @extend_schema(
        request=ProblemTranslationSerializer,
        responses={200: ProblemTranslationSerializer, 201: ProblemTranslationSerializer, 204: None},
    )
    @action(
        detail=True,
        methods=["put", "delete"],
        url_path=r"translations/(?P<locale>[a-z]{2,3})",
    )
    def translation(
        self, request: Request, slug: str | None = None, locale: str | None = None
    ) -> Response:
        """Create, replace or remove one language."""
        problem = self.get_object()
        if locale not in translations.LOCALES:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self._check_translation_write(problem)
        existing = ProblemTranslation.objects.filter(problem=problem, locale=locale).first()
        if request.method == "DELETE":
            if existing is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            existing.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if locale == problem.statement_locale:
            raise TranslationIsBase()
        serializer = ProblemTranslationSerializer(existing, data=request.data)
        serializer.is_valid(raise_exception=True)
        saved: Any = serializer.save(problem=problem, locale=locale)
        return Response(
            ProblemTranslationSerializer(saved).data,
            status=status.HTTP_200_OK if existing else status.HTTP_201_CREATED,
        )
