from __future__ import annotations

from typing import ClassVar

from core.staff import StaffViewSet
from quizzes.models import Question
from quizzes.staff_serializers import StaffQuestionSerializer


class StaffQuestionViewSet(StaffViewSet):
    """Savol banki — variantlar savol bilan birga (ichma-ich) tahrirlanadi."""

    queryset = Question.objects.prefetch_related("choices", "topics")
    serializer_class = StaffQuestionSerializer
    search_fields: ClassVar[list[str]] = ["text"]
    ordering_fields: ClassVar[list[str]] = ["pk", "difficulty", "created_at"]
