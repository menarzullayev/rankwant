from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db.models import Count, QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from contests import certificate_pdf
from contests.models import Certificate, Clarification, Contest, ContestRegistration, Standing
from contests.regional import cache_key, region_counts, regional_rows
from contests.serializers import (
    CertificateSerializer,
    ClarificationAnswerSerializer,
    ClarificationAskSerializer,
    ClarificationListSerializer,
    ClarificationSerializer,
    ContestAnnouncementSerializer,
    ContestDetailSerializer,
    ContestSerializer,
    ContestViewerSerializer,
    DisqualifySerializer,
    IntegrityReportSerializer,
    RegistrationSerializer,
    StandingSerializer,
)
from contests.services import start_virtual, virtual_deadline
from core.cache import cache_get, cache_set, edge_cacheable
from core.models import User
from core.openapi_docs import crud_summaries
from core.pagination import StandardPagination
from profiles.catalog import UZ_REGIONS

#: Chekka kesh oralig'i — 04-prd: standings 10–30 s da yangilansa yetarli.
#:
#: Ilgari bu yerda SSE oqimi turardi. Har ulanish gunicorn ning sinxron
#: ishchisini 300 soniyagacha band qilardi va o'lchandi: 4 ta tomoshabin
#: butun API ni javobsiz qoldirardi. Jadval hamma uchun bir xil, ya'ni
#: uni CDN keshlay oladi — 110 000 tomoshabin origin'ga 10 soniyada
#: bitta so'rov bo'lib tushadi. Mijozda polling allaqachon bor edi.
STANDINGS_CACHE_S = 10

#: Ommaviy jadval shuncha qator qaytaradi. Chegara KESH uchun: javob
#: hamma uchun bir xil bo'lgandagina CDN uni bir marta olib, hammaga
#: tarqata oladi. 500 qator ~45 KB (o'lchandi).
STANDINGS_TOP = 500


def _error(code: str, message: str, http: int, retry_after: int | None = None) -> Response:
    response = Response({"error": {"code": code, "message": message, "details": {}}}, status=http)
    if retry_after is not None:
        response["Retry-After"] = str(retry_after)
    return response


def _clar_error(exc: Any) -> Response:
    return _error(exc.code, exc.message, exc.status, exc.retry_after)


@crud_summaries(
    one="musobaqa",
    many="musobaqa",
    only=("list", "retrieve"),
    extra={
        "register": "Musobaqaga ro'yxatdan o'tish",
        "standings": "Turnik jadvali",
        "my_standing": "O'z o'rni",
        "virtual": "Virtual qatnashish",
        "viewer": "Mening musobaqadagi holatim",
        "clarifications": "Savol-javob va e'lonlar",
        "answer": "Savolga javob berish",
        "announcements": "E'lon qilish",
        "integrity": "Halol o'yin hisoboti",
        "disqualify": "Diskvalifikatsiya",
    },
)
class ContestViewSet(viewsets.ReadOnlyModelViewSet[Contest]):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    queryset = (
        Contest.objects.filter(is_public=True)
        .prefetch_related("problems__problem")
        .annotate(participant_count=Count("registrations", distinct=True))
        # An aggregate drops `Meta.ordering`; without this the pages would shuffle.
        .order_by("-start_at")
    )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ContestDetailSerializer if self.action == "retrieve" else ContestSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "region",
                str,
                description="Only this Uzbekistan region (`profiles.catalog.UZ_REGIONS`); "
                "each row then carries its regional place in `region_rank`.",
            )
        ],
        responses={200: StandingSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def standings(self, request: Request, slug: str | None = None) -> Response:
        contest = self.get_object()
        region = request.query_params.get("region", "")
        if region and region not in UZ_REGIONS:
            return _error("invalid_region", "Unknown region code.", status.HTTP_400_BAD_REQUEST)
        key = cache_key(contest.pk, region)
        payload = cache_get(key)
        if payload is None:
            # Insiders sit among the others with a star and no place
            # (ADR-0055, part 2): the table follows `position`, not `rank`.
            rows = (
                regional_rows(contest, region, STANDINGS_TOP)
                if region
                else Standing.objects.filter(contest=contest)
                .select_related("user")
                .order_by("position")[:STANDINGS_TOP]
            )
            payload = {
                "frozen": contest.is_frozen,
                "region": region,
                # The filter offers the regions that have participants.
                "regions": region_counts(contest),
                "results": StandingSerializer(rows, many=True).data,
            }
            cache_set(key, payload, STANDINGS_CACHE_S)
        # Jadval hamma uchun bir xil — Redis + chekka (core.cache).
        return edge_cacheable(Response(payload), STANDINGS_CACHE_S)

    @extend_schema(responses={200: StandingSerializer, 404: None})
    @action(
        detail=True,
        methods=["get"],
        url_path="standings/me",
        permission_classes=[IsAuthenticated],
    )
    def my_standing(self, request: Request, slug: str | None = None) -> Response:
        """Foydalanuvchining O'Z qatori — ommaviy jadvaldan alohida.

        Ommaviy jadval `STANDINGS_TOP` bilan cheklangan, ya'ni 10 000
        qatnashchili musobaqada 501-o'rindagi odam o'z natijasini umuman
        ko'ra olmasdi.

        Qatorni umumiy javobga qo'shib bo'lmaydi: o'shanda javob har
        foydalanuvchi uchun boshqacha bo'lib, CDN uni keshlay olmaydi va
        butun tomoshabin yuki origin'ga tushadi. Shuning uchun ALOHIDA,
        kichik va keshlanmaydigan so'rov.
        """
        contest = self.get_object()
        assert isinstance(request.user, User)
        row = (
            Standing.objects.filter(contest=contest, user=request.user)
            .select_related("user")
            .first()
        )
        if row is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(StandingSerializer(row).data)

    @extend_schema(responses={200: ContestViewerSerializer})
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def viewer(self, request: Request, slug: str | None = None) -> Response:
        """The visitor's own standing with the contest (ADR-0055, part 2).

        Their insider role, whether they are registered, and — for an
        insider before the start — the problems they test.
        """
        from contests.insiders import role_of

        contest = self.get_object()
        assert isinstance(request.user, User)
        role = role_of(contest, request.user)
        testing = bool(role) and timezone.now() < contest.start_at
        problems = contest.problems.select_related("problem") if testing else []
        from contests.integrity import can_judge

        registration = contest.registrations.filter(user=request.user).first()
        return Response(
            ContestViewerSerializer(
                {
                    "role": role,
                    "registered": registration is not None,
                    "testing": testing,
                    "problems": problems,
                    "disqualified_reason": registration.disqualified_reason
                    if registration is not None and registration.disqualified_at
                    else None,
                    "judge": can_judge(contest, request.user),
                }
            ).data
        )

    # ── Fair play (ADR-0055, part 4) ────────────────────────────────

    @extend_schema(responses={200: IntegrityReportSerializer})
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def integrity(self, request: Request, slug: str | None = None) -> Response:
        """The editor signals that stand out — for the jury, after the end."""
        from contests import integrity as fair

        contest = self.get_object()
        if not fair.can_judge(contest, request.user):
            return _error("forbidden", "Only the jury reads this", status.HTTP_403_FORBIDDEN)
        if not contest.is_finished:
            return _error("contest_running", "The report opens when the contest ends", 400)
        disqualified = contest.registrations.filter(disqualified_at__isnull=False).select_related(
            "user"
        )
        return Response(
            IntegrityReportSerializer(
                {
                    "results": fair.report(contest),
                    "disqualified": [
                        {
                            "username": r.user.username,
                            "reason": r.disqualified_reason,
                            "at": r.disqualified_at,
                        }
                        for r in disqualified
                    ],
                }
            ).data
        )

    @extend_schema(request=DisqualifySerializer, responses={200: RegistrationSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def disqualify(self, request: Request, slug: str | None = None) -> Response:
        from contests import integrity as fair

        contest = self.get_object()
        if not fair.can_judge(contest, request.user):
            return _error("forbidden", "Only the jury disqualifies", status.HTTP_403_FORBIDDEN)
        form = DisqualifySerializer(data=request.data)
        form.is_valid(raise_exception=True)
        target = User.objects.filter(username=form.validated_data["username"]).first()
        if target is None:
            return _error("user_not_found", "No such user", status.HTTP_404_NOT_FOUND)
        try:
            registration = fair.disqualify(
                contest, target, request.user, form.validated_data["reason"]
            )
        except fair.FairPlayError as exc:
            return _error(exc.code, exc.message, exc.status)
        return Response(RegistrationSerializer(registration).data)

    # ── Questions and announcements (ADR-0055, part 3) ──────────────

    def _clarifications(self, request: Request, contest: Contest) -> Response:
        from contests import clarifications as qa

        user = request.user
        moderator = qa.can_moderate(contest, user)
        signed_in = bool(user and user.is_authenticated)
        asked = (
            Clarification.objects.filter(contest=contest, author_id=user.pk).count()
            if signed_in
            else 0
        )
        rows = qa.visible(contest, user)[: qa.LIST_LIMIT]
        payload = {
            "moderator": moderator,
            "can_ask": signed_in and timezone.now() < contest.end_at,
            "questions_left": max(0, qa.MAX_QUESTIONS - asked) if signed_in else 0,
            "results": ClarificationSerializer(
                rows, many=True, context={"request": request, "moderator": moderator}
            ).data,
        }
        # Already serialized; `ClarificationListSerializer` describes it.
        return Response(payload)

    @extend_schema(methods=["GET"], request=None, responses={200: ClarificationListSerializer})
    @extend_schema(
        methods=["POST"],
        request=ClarificationAskSerializer,
        responses={201: ClarificationSerializer, 400: None, 429: None},
    )
    @action(detail=True, methods=["get", "post"], permission_classes=[AllowAny])
    def clarifications(self, request: Request, slug: str | None = None) -> Response:
        """Questions, answers and announcements; POST asks a question."""
        from contests import clarifications as qa

        contest = self.get_object()
        if request.method == "GET":
            return self._clarifications(request, contest)
        if not request.user.is_authenticated:
            return _error("not_authenticated", "Sign in to ask", status.HTTP_401_UNAUTHORIZED)
        form = ClarificationAskSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        try:
            row = qa.ask(
                contest,
                request.user,
                form.validated_data.get("problem"),
                form.validated_data["question"],
            )
        except qa.ClarificationError as exc:
            return _clar_error(exc)
        return Response(
            ClarificationSerializer(row, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=ClarificationAnswerSerializer, responses={200: ClarificationSerializer})
    @action(
        detail=True,
        methods=["post"],
        url_path=r"clarifications/(?P<row_id>\d+)/answer",
        permission_classes=[IsAuthenticated],
    )
    def answer(self, request: Request, slug: str | None = None, row_id: str = "") -> Response:
        from contests import clarifications as qa

        contest = self.get_object()
        if not qa.can_moderate(contest, request.user):
            return _error("forbidden", "Only the jury answers", status.HTTP_403_FORBIDDEN)
        row = get_object_or_404(Clarification, pk=row_id, contest=contest, author__isnull=False)
        form = ClarificationAnswerSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        try:
            qa.answer(
                row,
                request.user,
                form.validated_data.get("answer", ""),
                form.validated_data.get("answer_code", ""),
                form.validated_data["public"],
            )
        except qa.ClarificationError as exc:
            return _clar_error(exc)
        return Response(
            ClarificationSerializer(row, context={"request": request, "moderator": True}).data
        )

    @extend_schema(request=ContestAnnouncementSerializer, responses={201: ClarificationSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def announcements(self, request: Request, slug: str | None = None) -> Response:
        from contests import clarifications as qa

        contest = self.get_object()
        if not qa.can_moderate(contest, request.user):
            return _error("forbidden", "Only the jury announces", status.HTTP_403_FORBIDDEN)
        form = ContestAnnouncementSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        try:
            row = qa.announce(
                contest,
                request.user,
                form.validated_data.get("problem"),
                form.validated_data["text"],
            )
        except qa.ClarificationError as exc:
            return _clar_error(exc)
        return Response(
            ClarificationSerializer(row, context={"request": request, "moderator": True}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=None, responses={201: RegistrationSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def register(self, request: Request, slug: str | None = None) -> Response:
        contest = self.get_object()
        if contest.is_finished:
            return Response(
                {
                    "error": {
                        "code": "contest_finished",
                        "message": "The contest has finished",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        assert isinstance(request.user, User)
        reg, created = ContestRegistration.objects.get_or_create(contest=contest, user=request.user)
        return Response(
            RegistrationSerializer(reg).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(request=None, responses={201: RegistrationSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def virtual(self, request: Request, slug: str | None = None) -> Response:
        """PRD P1-1 — tugagan musobaqani o'z vaqtingizda boshlash.

        Virtual ishtirok reytingga ta'sir qilmaydi va rasmiy jadvalga
        kirmaydi (contests.services.rebuild_standings).
        """
        contest = self.get_object()
        assert isinstance(request.user, User)
        try:
            reg = start_virtual(contest, request.user)
        except ValueError as exc:
            return Response(
                {"error": {"code": "not_finished", "message": str(exc), "details": {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = RegistrationSerializer(reg).data
        data["deadline"] = virtual_deadline(reg)
        return Response(data, status=status.HTTP_201_CREATED)


# ── Sertifikatlar (ADR-0019) ─────────────────────────────────────────

#: PDF o'zgarmaydi (ism berilgan paytdagi holatda) — bir kun keshlanadi.
CERTIFICATE_PDF_TTL = 24 * 60 * 60


def _certificate(pk: UUID) -> Certificate:
    return get_object_or_404(
        Certificate.objects.select_related("user", "contest"), pk=pk, user__is_active=True
    )


@extend_schema(summary="Sertifikat ma'lumotlari")
class CertificateView(APIView):
    """Sertifikatni tekshirish — QR shu ma'lumotga olib keladi."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: CertificateSerializer})
    def get(self, request: Request, pk: UUID) -> Response:
        return Response(CertificateSerializer(_certificate(pk)).data)


class CertificatePdfView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Sertifikat PDF'i",
        responses={(200, "application/pdf"): OpenApiTypes.BINARY},
    )
    def get(self, request: Request, pk: UUID) -> HttpResponse:
        cert = _certificate(pk)
        key = f"cert:pdf:{cert.pk}"
        data: bytes | None = cache_get(key)
        if data is None:
            data = certificate_pdf.render(cert)
            cache_set(key, data, CERTIFICATE_PDF_TTL)
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="rankwant-{cert.contest.slug}-{cert.user.username}.pdf"'
        )
        return response


@extend_schema(summary="Foydalanuvchi sertifikatlari")
class UserCertificatesView(generics.ListAPIView[Certificate]):
    """Profildagi «Sertifikatlar» tabi."""

    permission_classes = [AllowAny]
    serializer_class = CertificateSerializer
    pagination_class = StandardPagination

    def get_queryset(self) -> QuerySet[Certificate]:
        if getattr(self, "swagger_fake_view", False):
            return Certificate.objects.none()
        user = get_object_or_404(User, username=self.kwargs["username"], is_active=True)
        return (
            Certificate.objects.filter(user=user)
            .select_related("user", "contest")
            .order_by("-contest__end_at", "-issued_at")
        )
