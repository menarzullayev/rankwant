from __future__ import annotations

from collections import Counter
from typing import Any

from django.db.models import Avg, Count, Exists, F, Max, Min, OuterRef, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User
from core.pagination import StandardPagination
from judging.verdicts import Verdict
from problems.filters import ProblemFilter
from problems.models import (
    DIFFICULTY_LEVELS,
    EditorialUnlock,
    Favourite,
    Language,
    Problem,
    ProblemRating,
    ProblemReport,
    ProblemVote,
    TestCase,
    Topic,
    difficulty_level,
)
from problems.recommend import recommend, target_difficulty
from problems.serializers import (
    LanguageSerializer,
    ProblemDetailSerializer,
    ProblemListSerializer,
    RateProblemSerializer,
    ReportProblemSerializer,
    TopicSerializer,
    VoteSerializer,
)
from qvant import ledger
from qvant.models import QvantTransaction


class ProblemViewSet(viewsets.ReadOnlyModelViewSet[Problem]):
    """Ommaviy masala arxivi.

    Yozish Django admin orqali (PRD P0-2) — API faqat o'qish uchun.
    """

    permission_classes = [AllowAny]
    lookup_field = "slug"
    filterset_class = ProblemFilter
    pagination_class = StandardPagination
    # `SearchFilter` YO'Q: `?search=` `ProblemFilter` da, chunki u
    # so'rovni normallashtirishi va mavzuni ham qamrashi kerak.
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = [
        "difficulty",
        "solved_count",
        "attempt_count",
        "view_count",
        "created_at",
    ]
    ordering = ["difficulty"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        # Baho ro'yxatda ham ko'rinadi — har qatorga alohida so'rov
        # bo'lmasligi uchun annotatsiya.
        return (
            Problem.objects.filter(is_public=True)
            .prefetch_related("topics")
            .annotate(
                rating_avg=Avg("ratings__score"),
                rating_count=Count("ratings", distinct=True),
                # `Exists` — `Count` emas: qo'shimcha JOIN boshqa
                # agregatlarni ko'paytirib yuborardi.
                has_tests=Exists(TestCase.objects.filter(problem=OuterRef("pk"))),
            )
            .order_by("difficulty", "slug")
        )

    def get_serializer_context(self):  # type: ignore[no-untyped-def]
        context: dict[str, Any] = dict(super().get_serializer_context())
        user = self.request.user
        if not user.is_authenticated:
            return context

        from judging.models import Attempt
        from problems.models import Favourite
        from ratings.models import UserSolvedProblem

        # Uchalasi ham foydalanuvchi bo'yicha bitta so'rov — qator soniga
        # bog'liq emas.
        context["solved_slugs"] = set(
            UserSolvedProblem.objects.filter(user=user).values_list("problem__slug", flat=True)
        )
        context["favourite_ids"] = set(
            Favourite.objects.filter(user=user).values_list("problem_id", flat=True)
        )
        context["unlocked_ids"] = set(
            EditorialUnlock.objects.filter(user=user).values_list("problem_id", flat=True)
        )
        # Oxirgi urinish verdikti — «urindim, WA oldim» signali. Ikkita
        # so'rov, ikkalasi ham urinilgan masalalar soni bilan chegaralangan
        # (`DISTINCT ON` Postgres'ga bog'lab qo'yardi, testlar SQLite'da).
        last_ids = dict(
            Attempt.objects.filter(user=user).values_list("problem_id").annotate(last=Max("pk"))
        )
        verdicts = dict(
            Attempt.objects.filter(pk__in=last_ids.values()).values_list("pk", "verdict")
        )
        context["my_verdicts"] = {
            problem_id: verdicts.get(attempt_id) for problem_id, attempt_id in last_ids.items()
        }
        return context

    def get_object(self) -> Problem:
        # Detal sahifada til, biriktirma va o'xshashlik ro'yxatlari
        # o'qiladi — har biri alohida so'rov bo'lib ketmasin.
        base = self.get_queryset()  # type: ignore[no-untyped-call]
        queryset = base.select_related("author").prefetch_related(
            "attachments", "languages__language", "similar_to__similar"
        )
        problem: Problem = get_object_or_404(queryset, slug=self.kwargs["slug"])
        return problem

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().retrieve(request, *args, **kwargs)
        # Bitta arzon UPDATE, o'qishdan keyin — sanoq xato bo'lsa ham
        # sahifa ochilishi buzilmasin.
        Problem.objects.filter(slug=kwargs.get("slug")).update(view_count=F("view_count") + 1)
        return response

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ProblemDetailSerializer if self.action == "retrieve" else ProblemListSerializer

    @extend_schema(request=None, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated])
    def favourite(self, request: Request, slug: str | None = None) -> Response:
        problem = self.get_object()
        assert isinstance(request.user, User)
        if request.method == "DELETE":
            Favourite.objects.filter(user=request.user, problem=problem).delete()
            return Response({"is_favourite": False})
        Favourite.objects.get_or_create(user=request.user, problem=problem)
        return Response({"is_favourite": True})

    @extend_schema(request=RateProblemSerializer, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated], url_path="rate")
    def rate(self, request: Request, slug: str | None = None) -> Response:
        problem = self.get_object()
        serializer = RateProblemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        ProblemRating.objects.update_or_create(
            user=request.user,
            problem=problem,
            defaults={"score": serializer.validated_data["score"]},
        )
        stats = problem.ratings.aggregate(average=Avg("score"), count=Count("pk"))
        return Response(
            {
                "average": round(stats["average"], 1) if stats["average"] else None,
                "count": stats["count"],
                "my_rating": serializer.validated_data["score"],
            }
        )

    @extend_schema(request=VoteSerializer, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def vote(self, request: Request, slug: str | None = None) -> Response:
        """Yoqdi / yoqmadi. `value=0` — ovozni olib tashlaydi."""
        problem = self.get_object()
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        value = serializer.validated_data["value"]
        if value:
            ProblemVote.objects.update_or_create(
                user=request.user, problem=problem, defaults={"value": value}
            )
        else:
            ProblemVote.objects.filter(user=request.user, problem=problem).delete()

        counts = Counter(problem.votes.values_list("value", flat=True))
        return Response(
            {
                "up": problem.likes_count + counts[ProblemVote.UP],
                "down": problem.dislikes_count + counts[ProblemVote.DOWN],
                "mine": value,
            }
        )

    @extend_schema(request=ReportProblemSerializer, responses={201: {"type": "object"}})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def report(self, request: Request, slug: str | None = None) -> Response:
        """Masaladagi nuqson haqida xabar.

        Takroriy bosish yangi yozuv YARATMAYDI — ochiq xabar bittadan
        ortiq bo'lmasligi indeks bilan kafolatlangan, bu yerda esa u
        shunchaki yangilanadi.
        """
        problem = self.get_object()
        serializer = ReportProblemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assert isinstance(request.user, User)
        ProblemReport.objects.update_or_create(
            user=request.user,
            problem=problem,
            status=ProblemReport.Status.OPEN,
            defaults=serializer.validated_data,
        )
        return Response({"reported": True}, status=201)

    @extend_schema(request=None, responses={200: {"type": "object"}})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def editorial(self, request: Request, slug: str | None = None) -> Response:
        """Tahlilni Qvant sarflab ochadi — ADR-0013.

        Yechgan odam bu yerga umuman kelmaydi: unga tahlil allaqachon
        ochiq. Shu sababli bu yo'l faqat «yechmadim, lekin ko'raman»
        holati uchun.
        """
        problem = self.get_object()
        assert isinstance(request.user, User)
        if not problem.editorial:
            return Response({"detail": "Bu masalada tahlil yo'q"}, status=404)

        already = EditorialUnlock.objects.filter(user=request.user, problem=problem).exists()
        if not already and problem.editorial_price:
            try:
                ledger.debit(
                    request.user,
                    problem.editorial_price,
                    QvantTransaction.Reason.PURCHASE,
                    ref_type="editorial",
                    ref_id=problem.slug,
                )
            except ledger.InsufficientBalance:
                return Response(
                    {"detail": f"Balans yetarli emas — {problem.editorial_price} Qvant kerak"},
                    status=402,
                )
            EditorialUnlock.objects.create(
                user=request.user, problem=problem, price=problem.editorial_price
            )
        return Response({"editorial": problem.editorial, "price": problem.editorial_price})


class RecommendationView(APIView):
    """PRD P1-2 — darajangizga mos, yechmagan masalalaringiz."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: ProblemListSerializer(many=True)})
    def get(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        limit = min(int(request.query_params.get("limit", 10)), 50)
        problems = recommend(request.user, limit=limit)
        return Response(
            {
                "target_difficulty": target_difficulty(request.user),
                "results": ProblemListSerializer(problems, many=True).data,
            }
        )


class ProblemStatsView(APIView):
    """Masala statistikasi — verdikt/til taqsimoti va yechganlar.

    Ochiq: raqamlar hech kimning manbasini oshkor qilmaydi.
    """

    permission_classes = [AllowAny]
    #: Yechganlar ro'yxati cheklanadi — ommabop masalada minglab bo'lishi
    #: mumkin, sahifada esa bir nechtasi kifoya.
    SOLVER_LIMIT = 50

    @extend_schema(responses={200: OpenApiResponse(description="Masala statistikasi")})
    def get(self, request: Request, slug: str) -> Response:
        from judging.models import Attempt

        problem = get_object_or_404(Problem, slug=slug, is_public=True)
        attempts = Attempt.objects.filter(problem=problem)

        verdicts = [
            {"verdict": row["verdict"], "count": row["n"]}
            for row in attempts.values("verdict").annotate(n=Count("pk")).order_by("-n")
        ]
        languages = [
            {"language": row["language__code"], "count": row["n"], "solved": row["ac"]}
            for row in attempts.values("language__code")
            .annotate(n=Count("pk"), ac=Count("pk", filter=Q(verdict=Verdict.AC)))
            .order_by("-n")
        ]

        # Har foydalanuvchining BIRINCHI AC si. `DISTINCT ON` Postgres'ga
        # bog'lab qo'yardi (testlar SQLite'da), shuning uchun eng erta
        # AC'lar id bo'yicha olinib, Python'da bir marta filtrlanadi.
        seen: set[int] = set()
        solvers = []
        for attempt in (
            attempts.filter(verdict=Verdict.AC)
            .select_related("user", "language")
            .order_by("pk")[: self.SOLVER_LIMIT * 4]
        ):
            if attempt.user_id in seen:
                continue
            seen.add(attempt.user_id)
            solvers.append(
                {
                    "username": attempt.user.username,
                    "language": attempt.language.code,
                    "time_ms": attempt.time_ms,
                    "memory_kb": attempt.memory_kb,
                    "created_at": attempt.created_at,
                }
            )
            if len(solvers) >= self.SOLVER_LIMIT:
                break

        # Eng tez yechim — TILMA-TIL. Python'ni C++ bilan bir jadvalda
        # taqqoslash ma'nosiz bo'lardi: farq yechimda emas, tilda.
        # Codeforces va RoboContest ikkalasi ham shu bo'limni ko'rsatadi
        # va u optimallashtirishga sabab beradi.
        fastest = []
        for row in languages:
            best = (
                attempts.filter(verdict=Verdict.AC, language__code=row["language"])
                .select_related("user")
                .order_by("time_ms", "pk")
                .first()
            )
            if best is not None:
                fastest.append(
                    {
                        "language": row["language"],
                        "username": best.user.username,
                        "time_ms": best.time_ms,
                        "memory_kb": best.memory_kb,
                        "created_at": best.created_at,
                    }
                )
        fastest.sort(key=lambda row: row["time_ms"])

        return Response(
            {
                "total": attempts.count(),
                "verdicts": verdicts,
                "languages": languages,
                "solvers": solvers,
                "fastest": fastest,
            }
        )


class ProblemSolversView(APIView):
    """Masalani yechganlar — alohida bo'lim (KEP dagi «Solvers»).

    Statistika verdikt taqsimotini ko'rsatadi, bu yerda esa ODAMLAR:
    kim, nechanchi urinishda va qanday kod bilan yechgan. Ikkalasi bir
    sahifada bo'lsa, ikkalasi ham siqilib qolardi.
    """

    permission_classes = [AllowAny]
    LIMIT = 50

    ORDERINGS = {
        "first": "solved_at",
        "fast": "time_ms",
        "short": "code_length",
        "tries": "attempts",
    }

    @extend_schema(responses={200: OpenApiResponse(description="Yechganlar ro'yxati")})
    def get(self, request: Request, slug: str) -> Response:
        from django.db.models.functions import Length

        from judging.models import Attempt

        problem = get_object_or_404(Problem, slug=slug, is_public=True)
        accepted = Attempt.objects.filter(problem=problem, verdict=Verdict.AC)

        # Har foydalanuvchining BIRINCHI AC si — `DISTINCT ON` Postgres'ga
        # bog'lab qo'yardi (testlar SQLite'da), shuning uchun eng erta
        # id'lar bitta agregat so'rov bilan olinadi.
        first_ids = list(
            accepted.values("user_id").annotate(first=Min("pk")).values_list("first", flat=True)
        )
        rows = list(
            Attempt.objects.filter(pk__in=first_ids)
            .select_related("user", "language")
            .annotate(code_length=Length("source_code"))
            .order_by("pk")[: self.LIMIT]
        )

        # Nechanchi urinishda yechgan: shu masaladagi, AC gacha bo'lgan
        # urinishlar. Faqat ko'rsatiladigan foydalanuvchilar bo'yicha,
        # ya'ni so'rov ro'yxat uzunligi bilan chegaralangan.
        first_ac = {row.user_id: row.pk for row in rows}
        tries: Counter[int] = Counter()
        for user_id, pk in Attempt.objects.filter(
            problem=problem, user_id__in=first_ac
        ).values_list("user_id", "pk"):
            if pk <= first_ac[user_id]:
                tries[user_id] += 1

        solvers = [
            {
                "username": row.user.username,
                "rating_skills": row.user.rating_skills,
                "language": row.language.code,
                "time_ms": row.time_ms,
                "memory_kb": row.memory_kb,
                "code_length": row.code_length,
                "attempts": tries[row.user_id],
                "solved_at": row.created_at,
            }
            for row in rows
        ]

        key = self.ORDERINGS.get(str(request.query_params.get("ordering", "first")))
        if key and key != "solved_at":
            solvers.sort(key=lambda row: row[key])  # type: ignore[arg-type,return-value]

        return Response({"count": len(first_ids), "results": solvers})


class ProgressView(APIView):
    """Daraja bo'yicha yechilganlar — arxiv yon panelidagi progress bloki.

    Mehmonda ham ochiladi: o'shanda faqat jami masalalar ko'rinadi va
    `solved` nol bo'ladi, ya'ni blok arxiv hajmini ko'rsatuvchi kartaga
    aylanadi.
    """

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiResponse(description="Daraja bo'yicha progress")})
    def get(self, request: Request) -> Response:
        totals: Counter[str] = Counter()
        for value in Problem.objects.filter(is_public=True).values_list("difficulty", flat=True):
            totals[difficulty_level(value)[0]] += 1

        solved: Counter[str] = Counter()
        if request.user.is_authenticated:
            from ratings.models import UserSolvedProblem

            for value in UserSolvedProblem.objects.filter(
                user=request.user, problem__is_public=True
            ).values_list("problem__difficulty", flat=True):
                solved[difficulty_level(value)[0]] += 1

        levels = [
            {"code": code, "label": label, "total": totals[code], "solved": solved[code]}
            for _, code, label in DIFFICULTY_LEVELS
        ]
        return Response(
            {
                "levels": levels,
                "total": sum(totals.values()),
                "solved": sum(solved.values()),
            }
        )


class TopicSkillsView(APIView):
    """Mavzu kesimidagi kuch — Codeforces API tahlilidan kelgan g'oya.

    `rating_skills` bitta raqam va u «keyin nima qilay?» degan savolga
    javob bermaydi. Mavzu kesimi beradi: «graflarda uch marta urindingiz,
    bittasi ham yechilmagan» — bu aniq keyingi qadam.

    Formula GLOBAL Skills bilan bir xil (`skills_rating`, ADR-0006/0007),
    faqat mavzu bo'yicha ajratilgan — shunda ikki raqam bir-biriga zid
    kelmaydi va principle #2 saqlanadi.
    """

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiResponse(description="Mavzu bo'yicha kuch")})
    def get(self, request: Request) -> Response:
        from ratings.formulas import skills_rating
        from ratings.models import UserSolvedProblem

        solved_ids: set[int] = set()
        attempted_ids: set[int] = set()
        if request.user.is_authenticated:
            from judging.models import Attempt

            solved_ids = set(
                UserSolvedProblem.objects.filter(user=request.user).values_list(
                    "problem_id", flat=True
                )
            )
            attempted_ids = set(
                Attempt.objects.filter(user=request.user)
                .values_list("problem_id", flat=True)
                .distinct()
            )

        # Bitta so'rov: (masala, qiyinlik, mavzu). Mavzu soniga qarab
        # so'rov ko'paymaydi — arxivda 148 ta mavzu bor.
        rows = Problem.objects.filter(is_public=True).values_list(
            "pk", "difficulty", "topics__slug", "topics__name_uz"
        )

        totals: Counter[str] = Counter()
        labels: dict[str, str] = {}
        solved_difficulties: dict[str, list[int]] = {}
        attempted: Counter[str] = Counter()
        for problem_id, difficulty, slug, label in rows:
            if slug is None:  # mavzusiz masala
                continue
            totals[slug] += 1
            labels[slug] = label
            if problem_id in solved_ids:
                solved_difficulties.setdefault(slug, []).append(difficulty)
            elif problem_id in attempted_ids:
                attempted[slug] += 1

        topics: list[dict[str, Any]] = [
            {
                "slug": slug,
                "label": labels[slug],
                "total": total,
                "solved": len(solved_difficulties.get(slug, [])),
                # Urinilgan, LEKIN yechilmagan — «taqalib qolgan» signali.
                "stuck": attempted[slug],
                "rating": skills_rating(solved_difficulties.get(slug, [])),
            }
            for slug, total in totals.items()
        ]
        topics.sort(key=lambda row: (-int(row["rating"]), -int(row["solved"]), str(row["slug"])))
        return Response({"topics": topics})


class TopicViewSet(viewsets.ReadOnlyModelViewSet[Topic]):
    """Filtr paneli uchun mavzular.

    Faqat OMMAVIY masalasi bori: import qilingan arxiv 140 dan ortiq
    teg olib keladi va ularning ko'pi hali qoralamalarga tegishli —
    hech narsa topmaydigan yorliq filtrni shovqinga aylantiradi.
    Xodimlar to'liq ro'yxatni `staff/topics/` da ko'radi.
    """

    permission_classes = [AllowAny]
    serializer_class = TopicSerializer
    lookup_field = "slug"
    queryset = Topic.objects.filter(problems__is_public=True).distinct().order_by("slug")


class LanguageViewSet(viewsets.ReadOnlyModelViewSet[Language]):
    permission_classes = [AllowAny]
    serializer_class = LanguageSerializer
    lookup_field = "code"
    queryset = Language.objects.filter(is_active=True).order_by("name")
