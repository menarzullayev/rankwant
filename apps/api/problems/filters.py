from __future__ import annotations

import django_filters as filters

from problems.models import DIFFICULTY_LEVELS, Problem


class ProblemFilter(filters.FilterSet):  # type: ignore[misc]
    """PRD P0-2: qiyinlik / mavzu / til bo'yicha filtr."""

    difficulty__gte = filters.NumberFilter(field_name="difficulty", lookup_expr="gte")
    difficulty__lte = filters.NumberFilter(field_name="difficulty", lookup_expr="lte")
    topics = filters.CharFilter(field_name="topics__slug", lookup_expr="iexact")
    level = filters.ChoiceFilter(
        choices=[(code, label) for _, code, label in DIFFICULTY_LEVELS],
        method="filter_level",
    )

    class Meta:
        model = Problem
        fields = ["difficulty", "checker_type"]

    def filter_level(self, queryset, name: str, value: str):  # type: ignore[no-untyped-def]
        lower = 0
        for upper, code, _label in DIFFICULTY_LEVELS:
            if code == value:
                return queryset.filter(difficulty__gte=lower, difficulty__lt=upper)
            lower = upper
        return queryset
