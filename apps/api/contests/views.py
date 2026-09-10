from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from contests.models import Contest, ContestRegistration, Standing
from contests.serializers import (
    ContestDetailSerializer,
    ContestSerializer,
    RegistrationSerializer,
    StandingSerializer,
)
from contests.services import start_virtual, virtual_deadline
from core.cache import edge_cacheable
from core.models import User

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


class ContestViewSet(viewsets.ReadOnlyModelViewSet[Contest]):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    queryset = Contest.objects.filter(is_public=True).prefetch_related("problems__problem")

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        return ContestDetailSerializer if self.action == "retrieve" else ContestSerializer

    @extend_schema(responses={200: StandingSerializer(many=True)})
    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def standings(self, request: Request, slug: str | None = None) -> Response:
        contest = self.get_object()
        rows = (
            Standing.objects.filter(contest=contest)
            .select_related("user")
            .order_by("rank")[:STANDINGS_TOP]
        )
        # Jadval hamma uchun bir xil — chekkada keshlanadi (core.cache).
        return edge_cacheable(
            Response(
                {
                    "frozen": contest.is_frozen,
                    "results": StandingSerializer(rows, many=True).data,
                }
            ),
            STANDINGS_CACHE_S,
        )

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

    @extend_schema(request=None, responses={201: RegistrationSerializer})
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def register(self, request: Request, slug: str | None = None) -> Response:
        contest = self.get_object()
        if contest.is_finished:
            return Response(
                {
                    "error": {
                        "code": "contest_finished",
                        "message": "Musobaqa tugagan",
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
