from __future__ import annotations

import django_filters as filters
from django.db.models import Q

from problems.models import DIFFICULTY_LEVELS, Problem, normalize_search


class ProblemFilter(filters.FilterSet):  # type: ignore[misc]
    """PRD P0-2: qiyinlik / mavzu / til bo'yicha filtr."""

    # Qidiruv DRF `SearchFilter` da emas, shu yerda: so'rovni ham,
    # sarlavhani ham bir ko'rinishga keltirish kerak, aks holda qaysi
    # apostrofni yozganingizga qarab natija o'zgarardi.
    search = filters.CharFilter(method="filter_search")
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
    #: Urinish bo'lganmi. `solved=false` bilan birga «taqalib qolganlar»
    #: ni beradi — o'rganish uchun eng foydali ro'yxat.
    attempted = filters.BooleanFilter(method="filter_attempted")
    favourite = filters.BooleanFilter(method="filter_favourite")
    # Tavsiya alohida sahifa emas, arxivning bir rejimi: filtr, saralash va
    # sahifalash o'sha-o'sha ishlayveradi.
    recommended = filters.BooleanFilter(method="filter_recommended")

    class Meta:
        model = Problem
        fields = ["difficulty", "checker_type", "statement_locale"]

    def filter_search(self, queryset, name: str, value: str):  # type: ignore[no-untyped-def]
        """Sarlavha, slug va MAVZU bo'yicha qidiradi.

        Mavzu ham qidiriladi, chunki «dinamik» deb yozgan odam
        «Dinamik dasturlash» masalalarini kutadi — 109 ta mavzudan
        filtr panelida tanlashdan ko'ra tezroq. Mavzu tomonida `slug`
        ishlatiladi: u allaqachon apostrofsiz va kichik harfda, ya'ni
        normallashtirilgan shaklning o'zi.
        """
        needle = normalize_search(value)
        if not needle:
            return queryset
        hyphenated = needle.replace(" ", "-")
        return queryset.filter(
            Q(title_search__icontains=needle)
            | Q(slug__icontains=hyphenated)
            | Q(topics__slug__icontains=hyphenated)
        ).distinct()

    def filter_solved(self, queryset, name: str, value: bool):  # type: ignore[no-untyped-def]
        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated:
            return queryset

        from ratings.models import UserSolvedProblem

        solved = UserSolvedProblem.objects.filter(user=user).values("problem_id")
        return queryset.filter(pk__in=solved) if value else queryset.exclude(pk__in=solved)

    def filter_attempted(self, queryset, name: str, value: bool):  # type: ignore[no-untyped-def]
        user = getattr(self.request, "user", None)
        if user is None or not user.is_authenticated:
            return queryset

        from judging.models import Attempt

        tried = Attempt.objects.filter(user=user).values("problem_id")
        return queryset.filter(pk__in=tried) if value else queryset.exclude(pk__in=tried)

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
