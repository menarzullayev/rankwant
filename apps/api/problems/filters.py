from __future__ import annotations

import django_filters as filters

from problems.models import DIFFICULTY_LEVELS, Problem


class ProblemFilter(filters.FilterSet):  # type: ignore[misc]
    """PRD P0-2: qiyinlik / mavzu / til bo'yicha filtr."""

    difficulty__gte = filters.NumberFilter(field_name="difficulty", lookup_expr="gte")
    difficulty__lte = filters.NumberFilter(field_name="difficulty", lookup_expr="lte")
    # Vergul bilan bir nechta mavzu: `?topics=dp,trees` — HAMMASI bo'lgan
    # masalalar (Codeforces `?tags=` bilan bir xil). Bitta qiymat ham shu
    # yo'l bilan ishlaydi.
    topics = filters.CharFilter(method="filter_topics")
    level = filters.ChoiceFilter(
        choices=[(code, label) for _, code, label in DIFFICULTY_LEVELS],
        method="filter_level",
    )

    # Yechilgan/yechilmagan — uchala taqqoslangan platformada ham bor.
    # Mehmon uchun ma'nosiz: filtr qo'llanmaydi, arxiv to'liq ko'rinadi.
    solved = filters.BooleanFilter(method="filter_solved")
    favourite = filters.BooleanFilter(method="filter_favourite")
    # Tavsiya alohida sahifa emas, arxivning bir rejimi: filtr, saralash va
    # sahifalash o'sha-o'sha ishlayveradi.
    recommended = filters.BooleanFilter(method="filter_recommended")

    class Meta:
        model = Problem
        fields = ["difficulty", "checker_type", "statement_locale"]

    def filter_solved(self, queryset, name: str, value: bool):  # type: ignore[no-untyped-def]
        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated:
            return queryset

        from ratings.models import UserSolvedProblem

        solved = UserSolvedProblem.objects.filter(user=user).values("problem_id")
        return queryset.filter(pk__in=solved) if value else queryset.exclude(pk__in=solved)

    def filter_topics(self, queryset, name: str, value: str):  # type: ignore[no-untyped-def]
        """Tanlangan mavzularning HAMMASI bo'lgan masalalar.

        Ilgari `__in` edi, ya'ni YOKI: «dp» va «daraxtlar» ni birga
        tanlagan odam ikkalasining yig'indisini olardi. Yettita masalada
        farqi yo'q edi, 2089 tasida esa bu filtrni ishdan chiqaradi —
        «daraxtlardagi dinamika» aniq so'rov, «dinamika yoki daraxtlar»
        esa arxivning yarmi. Codeforces `?tags=` ham shunday ishlaydi.

        Har mavzu alohida `filter()` bo'lishi SHART: bitta chaqiruvdagi
        `__in` M2M da hech qachon VA bermaydi.
        """
        for slug in (part.strip() for part in value.split(",") if part.strip()):
            queryset = queryset.filter(topics__slug=slug)
        return queryset.distinct()

    def filter_favourite(self, queryset, name: str, value: bool):  # type: ignore[no-untyped-def]
        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated or not value:
            return queryset
        return queryset.filter(favourites__user=user)

    def filter_recommended(self, queryset, name: str, value: bool):  # type: ignore[no-untyped-def]
        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated or not value:
            return queryset

        from problems.recommend import recommend

        return queryset.filter(pk__in=recommend(user, limit=50).values("pk"))

    def filter_level(self, queryset, name: str, value: str):  # type: ignore[no-untyped-def]
        lower = 0
        for upper, code, _label in DIFFICULTY_LEVELS:
            if code == value:
                return queryset.filter(difficulty__gte=lower, difficulty__lt=upper)
            lower = upper
        return queryset
