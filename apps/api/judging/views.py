from __future__ import annotations

from typing import Any, Never

from django.db.models import BooleanField, Case, Count, Q, QuerySet, Value, When
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.openapi_docs import crud_summaries
from core.pagination import SortableCursorPagination
from core.permissions import CanSubmit
from core.throttling import ResilientScopedRateThrottle
from hacks.services import can_view_source
from judging import answers
from judging.models import Attempt, CustomRun
from judging.serializers import (
    AttemptCreateSerializer,
    AttemptDetailSerializer,
    AttemptSerializer,
    CustomRunCreateSerializer,
    CustomRunSerializer,
)
from judging.services import enqueue, enqueue_custom
from judging.verdicts import Verdict
from problems.models import Language, Problem

#: Rad etilgan yuborishning manbasi tarix uchun saqlanadi, lekin to'liq
#: emas: bu qator natija emas, iz.
MAX_SOURCE_CHARS = 4096

#: Urinishlar ro'yxatida saralash mumkin bo'lgan maydonlar.
#:
#: Faqat sonli ustunlar: `username`, `verdict`, `language` ni saralash
#: 891 qatorli oqimda ma'noli emas, ustiga ular bo'yicha saralash
#: indekssiz — ya'ni har so'rov `attempt_problem_feed` ni tashlab,
#: to'liq saralashga o'tardi. Ro'yxatda yo'q qiymat standart tartibni
#: qaytaradi (foydalanuvchi satri `order_by()` ga yetib bormaydi).
ATTEMPT_ORDERINGS = {
    "created_at": "created_at",
    "-created_at": "-created_at",
    "time_ms": "time_ms",
    "-time_ms": "-time_ms",
    "memory_kb": "memory_kb",
    "-memory_kb": "-memory_kb",
    "source_size": "source_size",
    "-source_size": "-source_size",
}


class AttemptCursorPagination(SortableCursorPagination):
    ordering_fields = ATTEMPT_ORDERINGS


def _outside_the_freeze(qs: QuerySet[Attempt], viewer: Any) -> QuerySet[Attempt]:
    """Drop what a frozen contest hides from this viewer (ADR-0055).

    Attempts made after a contest's scoreboard froze are shown to their
    authors only, until the contest ends. Staff see everything.
    """
    if viewer.is_authenticated and viewer.is_staff:
        return qs
    from contests.services import frozen_windows

    for contest_id, freeze_at in frozen_windows():
        hidden = Q(contest_id=contest_id, created_at__gte=freeze_at)
        if viewer.is_authenticated:
            hidden &= ~Q(user=viewer)
        qs = qs.exclude(hidden)
    return qs


@crud_summaries(one="urinish", many="urinishlar", only=("list", "retrieve", "create"))
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                enum=sorted(ATTEMPT_ORDERINGS),
                description=(
                    "Saralash maydoni (`-` teskari tartib). Notanish qiymat "
                    "jim rad etiladi va standart tartib qaytadi."
                ),
            )
        ]
    )
)
class AttemptViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet[Attempt],
):
    """Submit va urinishlar tarixi — PRD P0-3."""

    pagination_class = AttemptCursorPagination
    #: `OrderingFilter` (global sukut) shu ro'yxatni tekshiradi. Usiz u
    #: SERIALIZER maydonlaridan ruxsat ro'yxatini yasardi va
    #: `?ordering=user__username` qabul qilinardi — ya'ni har so'rov
    #: `core_user` ga join qilib, butun ro'yxatni saralardi.
    #: Sahifalagich ham AYNAN shu to'plamni biladi; ikkisi ajralmasin.
    ordering_fields = list(ATTEMPT_ORDERINGS)
    throttle_scope = "submit"

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return [IsAuthenticated(), CanSubmit()]
        return [AllowAny()]

    def throttled(self, request: Request, wait: float) -> Never:
        """Shift urilganini TARIXGA yozadi, keyin odatdagidek 429 beradi.

        Ilgari rad etilgan yuborish hech qanday iz qoldirmasdi:
        foydalanuvchi «yubordim, qayoqqa ketdi?» degan savol bilan
        qolardi. Endi urinishlar ro'yxatida `RATE_LIMITED` ko'rinadi.

        Bitta portlash — BITTA qator: aks holda sekundiga yuzlab rad
        etilgan so'rov shuncha qator yasab, bazani to'ldirish yo'liga
        aylanardi. Oxirgi urinish allaqachon `RATE_LIMITED` bo'lsa,
        yangisi yozilmaydi.
        """
        data = request.data if isinstance(request.data, dict) else {}
        if self.action == "create" and request.user.is_authenticated:
            oxirgi = (
                Attempt.objects.filter(user=request.user).order_by("-created_at", "-pk").first()
            )
            if oxirgi is None or oxirgi.verdict != Verdict.RATE_LIMITED:
                problem = Problem.objects.filter(slug=data.get("problem")).first()
                language = Language.objects.filter(code=data.get("language")).first()
                if problem and language:
                    Attempt.objects.create(
                        user=request.user,
                        problem=problem,
                        language=language,
                        source_code=str(data.get("source_code", ""))[:MAX_SOURCE_CHARS],
                        verdict=Verdict.RATE_LIMITED,
                        judged_at=timezone.now(),
                    )
        super().throttled(request, wait)

    def get_throttles(self):  # type: ignore[no-untyped-def]
        return [ResilientScopedRateThrottle()] if self.action == "create" else []

    def get_queryset(self):  # type: ignore[no-untyped-def]
        params = self.request.query_params
        # `contest` ham SHU YERDA: serializer uning slug'ini beradi va
        # usiz har qator uchun alohida so'rov ketardi (N+1).
        qs = Attempt.objects.select_related("user", "problem", "language", "contest")

        # Schema generation builds this queryset with no request and, on CI,
        # no database: the freeze lookup would fail there and the generator
        # would lose the model (and with it the type of `id`).
        if not getattr(self, "swagger_fake_view", False):
            qs = _outside_the_freeze(qs, self.request.user)

        problem = params.get("problem")
        if problem:
            # ID bo'yicha — `problem__slug` ATAYIN emas. Join qo'shilishi
            # bilan Postgres `attempt_problem_feed` (problem, -created_at)
            # indeksidan foydalana olmay qoladi: u masalaning BARCHA
            # urinishlarini skanerlab, keyin saralab 26 tasini oladi.
            # O'lchandi (50 852 urinishli masala): 86.4 ms → 2.2 ms,
            # 156 881 bufer sahifasi o'rniga bir nechta.
            # A number names a problem too (`12`, `#12`): the feed's filter
            # takes what a person types, and nobody types a slug.
            number = problem.removeprefix("#")
            wanted = Problem.objects.filter(slug=problem)
            if number.isdigit() and len(number) <= 9:
                wanted = Problem.objects.filter(
                    Q(slug=problem) | Q(code=int(number), is_public=True)
                )
            problem_ids = wanted.values("pk")[:1]
            qs = qs.filter(problem_id=problem_ids)
            #: «Birinchi yechim» nishoni (S06). BITTA subquery butun
            #: sahifa uchun. `Exists()` bilan yozilsa u har qatorga
            #: bog'langan bo'lardi — 25 qatorli sahifada 25 marta.
            #: Faqat masala bo'yicha filtrlashda ma'noli: usiz
            #: «birinchi» tushunchasi butun platforma bo'ylab bo'lardi.
            first_ac = (
                Attempt.objects.filter(problem_id=problem_ids, verdict=Verdict.AC)
                .order_by("created_at", "pk")
                .values("pk")[:1]
            )
            qs = qs.annotate(
                is_first_solver=Case(
                    When(pk__in=first_ac, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        username = params.get("username")
        if username:
            # Bu yerda esa join TEZROQ (o'lchandi: 6.0 ms, ID bilan 17.3) —
            # foydalanuvchi bo'yicha alohida indeks yo'q va rejalashtiruvchi
            # join'li shaklda yaxshiroq reja tanlaydi.
            qs = qs.filter(user__username=username)

        # Ommabop masalada urinish minglab bo'ladi va filtrsiz ro'yxat
        # o'qib bo'lmaydigan oqimga aylanadi (KEP ham verdikt, til va
        # «faqat meniki» filtrlarini beradi).
        verdict = params.get("verdict")
        if verdict:
            # Vergulli ro'yxat: `RE` ikkiga ajratilgandan keyin bitta
            # «Bajarilishda xato» filtri eski `RE` ni ham, yangi
            # `RE_SIGNAL`/`RE_EXIT` ni ham qamrashi kerak.
            qs = qs.filter(verdict__in=[v for v in verdict.split(",") if v])
        language = params.get("language")
        if language:
            qs = qs.filter(language__code=language)
        if params.get("mine") in ("true", "1"):
            # A guest has no attempts. Ignoring the filter instead answered
            # "mine" with everybody's — a signed-out tab, or a server-side
            # request that lost its cookie, showed a list that looked right.
            user = self.request.user
            qs = qs.filter(user=user) if user.is_authenticated else qs.none()

        # Tartibni SAHIFALAGICH qo'yadi (`AttemptCursorPagination`), bu
        # yerdagi `order_by` esa sukut: kursor pozitsiyasi shu maydondan
        # olinadi, shuning uchun ikkisi ajralib ketmasligi kerak.
        return qs.order_by("-created_at")

    @extend_schema(
        summary="Foydalanuvchining masalalar bo'yicha urinishlar soni",
        parameters=[
            OpenApiParameter("username", str, required=True),
            OpenApiParameter("problems", str, required=True, description="Comma-separated slugs."),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=False, methods=["get"], pagination_class=None)
    def counts(self, request: Request) -> Response:
        """How many times one user submitted to each of a few problems.

        The list is cursor-paginated and carries no total, so a feed that
        folds attempts into one line per problem cannot count them from a
        page: it would print the page size. The attempts themselves are
        public, so their count is too.
        """
        username = request.query_params.get("username", "")
        slugs = [s for s in request.query_params.get("problems", "").split(",") if s]
        if not username or not slugs:
            return Response({})
        rows = (
            Attempt.objects.filter(
                user__username=username, problem__slug__in=slugs[: self.COUNTS_MAX]
            )
            .values_list("problem__slug")
            .annotate(n=Count("pk"))
        )
        return Response(dict(rows))

    #: Slugs one `counts` call answers; the feed asks for a handful.
    COUNTS_MAX = 20

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return AttemptCreateSerializer
        return AttemptDetailSerializer if self.action == "retrieve" else AttemptSerializer

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # The same freeze as the list: an attempt's number is easy to guess.
        attempt = get_object_or_404(
            _outside_the_freeze(Attempt.objects.all(), request.user), pk=kwargs["pk"]
        )
        data = AttemptDetailSerializer(attempt).data
        # Manba faqat egasiga va adminlarga ko'rinadi (IDOR himoyasi).
        if not (
            request.user.is_authenticated
            and (
                request.user.pk == attempt.user_id
                or request.user.is_staff
                # Hack oynasi ochiq va so'rovchi huquqli bo'lsa — aynan shu
                # yechim ochiladi (ADR-0020, 2-tamoyil). Bu umumiy
                # yopiqlikni almashtirmaydi, ustiga nuqtali istisno qo'yadi:
                # hack qilish uchun kodni ko'rish SHART.
                or can_view_source(request.user, attempt)
            )
        ):
            data.pop("source_code", None)
            data.pop("compile_output", None)
        return Response(data)

    @extend_schema(request=AttemptCreateSerializer, responses={201: AttemptSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = AttemptCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        assert isinstance(request.user, User)
        attempt = Attempt.objects.create(
            user=request.user,
            problem=Problem.objects.get(slug=data["problem"]),
            language=Language.objects.get(code=data["language"]),
            source_code=data["source_code"],
            contest=data.get("contest_obj"),
            verdict=Verdict.PENDING,
        )
        # Attempt AVVAL saqlanadi, keyin navbatga — navbat yiqilsa ham
        # submission yo'qolmaydi (10-operations § recovery).
        enqueue(attempt)
        return Response(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Javob fayllarini yuborish",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "problem": {"type": "string"},
                    "contest": {"type": "string"},
                    "archive": {"type": "string", "format": "binary"},
                    "files": {"type": "array", "items": {"type": "string", "format": "binary"}},
                },
                "required": ["problem"],
            }
        },
        responses={201: AttemptSerializer},
    )
    @action(detail=False, methods=["post"], url_path="answers", parser_classes=[MultiPartParser])
    def answer_files(self, request: Request) -> Response:
        """Submit to an `answer` problem: one text file per test, or a zip.

        A separate door from `create`: that one takes source code as JSON,
        this one takes files. A test left out keeps the solver's last
        answer for it (`judging/answers.py`).
        """
        form = request.POST
        serializer = AttemptCreateSerializer(
            data={
                "problem": form.get("problem", ""),
                "language": answers.ANSWER_LANGUAGE,
                "source_code": "-",
                **({"contest": form["contest"]} if form.get("contest") else {}),
            },
            context={"request": request, "answer_files": True},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        problem = Problem.objects.get(slug=data["problem"])

        archive = request.FILES.get("archive")
        uploads = request.FILES.getlist("files")
        # Refused by declared size before anything is read into memory.
        if sum(item.size or 0 for item in [*uploads, *([archive] if archive else [])]) > (
            answers.MAX_BYTES
        ):
            raise serializers.ValidationError(
                {"files": f"The upload exceeds {answers.MAX_BYTES // 1024 // 1024} MB"}
            )
        try:
            submitted = answers.read_upload(
                answers.judged_orders(problem),
                archive.read() if archive else None,
                [(item.name or "", item.read()) for item in uploads],
            )
        except answers.AnswerError as error:
            raise serializers.ValidationError({"files": str(error)}) from None

        assert isinstance(request.user, User)
        attempt = answers.submit(request.user, problem, submitted, contest=data.get("contest_obj"))
        enqueue(attempt)
        return Response(AttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


@crud_summaries(one="namunaviy yugurish", many="namunaviy yugurishlar", only=("create", "retrieve"))
class CustomRunViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet[CustomRun],
):
    """PRD P0-4 — custom test.

    Attempt EMAS: tarixga tushmaydi, reytingga ta'sir qilmaydi. Submit bilan
    bir xil rate limit qo'llanadi — bu ham judge resursini yeydi.
    """

    permission_classes = [IsAuthenticated, CanSubmit]
    throttle_scope = "submit"

    def get_throttles(self):  # type: ignore[no-untyped-def]
        return [ResilientScopedRateThrottle()] if self.action == "create" else []

    def get_queryset(self) -> QuerySet[CustomRun]:
        # Faqat o'z ishga tushirishlaringiz ko'rinadi. Sxema
        # generatsiyasida `request.user` — AnonymousUser (o'lchandi
        # 2026-09-24: "could not derive type of path parameter id").
        if getattr(self, "swagger_fake_view", False):
            return CustomRun.objects.none()
        assert isinstance(self.request.user, User)
        return CustomRun.objects.filter(user=self.request.user).select_related("language")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return CustomRunCreateSerializer if self.action == "create" else CustomRunSerializer

    @extend_schema(request=CustomRunCreateSerializer, responses={201: CustomRunSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = CustomRunCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        assert isinstance(request.user, User)
        run = CustomRun.objects.create(
            user=request.user,
            language=Language.objects.get(code=data["language"]),
            source_code=data["source_code"],
            stdin=data["stdin"],
            verdict=Verdict.PENDING,
        )
        enqueue_custom(run)
        return Response(CustomRunSerializer(run).data, status=status.HTTP_201_CREATED)
