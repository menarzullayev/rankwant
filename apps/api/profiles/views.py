"""Profil API'si: ko'nikma, karyera, tashqi profil, obuna, jamoa va ommaviy profil."""

from __future__ import annotations

from functools import partial
from typing import Any

from django.db import transaction
from django.db.models import F, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import exceptions, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from contests.models import Standing
from core.models import User
from core.pagination import StandardPagination
from core.tasks import queue
from profiles import achievements, external, public, stats, teams
from profiles.catalog import TECHNOLOGIES
from profiles.models import (
    Education,
    ExternalProfile,
    Follow,
    Skill,
    Team,
    UserSkill,
    UserTechnology,
    WorkExperience,
)
from profiles.serializers import (
    EducationSerializer,
    ExternalInSerializer,
    ExternalOutSerializer,
    FollowerSerializer,
    SkillSerializer,
    TeamCreateSerializer,
    TeamJoinSerializer,
    TeamSerializer,
    UserSkillInSerializer,
    UserSkillOutSerializer,
    WorkSerializer,
)
from profiles.tasks import refresh_external

#: Har bir ro'yxatning chegarasi — sahifa cheksiz uzun bo'lib ketmasin.
MAX_ROWS = 20


def _me(request: Request) -> User:
    assert isinstance(request.user, User)
    return request.user


def _list_body(request: Request) -> list[Any]:
    """PUT butun ro'yxatni almashtiradi — KEP'dagi «Saqlash» kabi."""
    data = request.data
    if not isinstance(data, list):
        raise exceptions.ValidationError({"detail": "Ro'yxat kutilgan"})
    if len(data) > MAX_ROWS:
        raise exceptions.ValidationError({"detail": f"Ko'pi bilan {MAX_ROWS} ta"})
    return data


def _profile_owner(username: str) -> User:
    return get_object_or_404(User, username=username, is_active=True)


# ── Kataloglar ───────────────────────────────────────────────────────


class SkillCatalogView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Ko'nikmalar katalogi", responses={200: SkillSerializer(many=True)})
    def get(self, request: Request) -> Response:
        return Response(SkillSerializer(Skill.objects.all(), many=True).data)


class TechnologyCatalogView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Texnologiyalar katalogi", responses={200: None})
    def get(self, request: Request) -> Response:
        return Response([{"slug": s, "name": n} for s, n in TECHNOLOGIES.items()])


# ── O'z profili ──────────────────────────────────────────────────────


class MySkillsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Ko'nikmalar ro'yxati", responses={200: UserSkillOutSerializer(many=True)}
    )
    def get(self, request: Request) -> Response:
        rows = UserSkill.objects.filter(user=_me(request)).select_related("skill")
        return Response(UserSkillOutSerializer(rows, many=True).data)

    @extend_schema(
        summary="Ko'nikmalarni almashtirish",
        request=UserSkillInSerializer(many=True),
        responses={200: UserSkillOutSerializer(many=True)},
    )
    def put(self, request: Request) -> Response:
        user = _me(request)
        serializer = UserSkillInSerializer(data=_list_body(request), many=True)
        serializer.is_valid(raise_exception=True)
        rows: list[dict[str, Any]] = serializer.validated_data
        slugs = [row["skill"] for row in rows]
        if len(set(slugs)) != len(slugs):
            raise exceptions.ValidationError({"detail": "Ko'nikma takrorlangan"})
        catalog = {skill.slug: skill for skill in Skill.objects.filter(slug__in=slugs)}
        unknown = [slug for slug in slugs if slug not in catalog]
        if unknown:
            raise exceptions.ValidationError({"detail": f"Noma'lum ko'nikma: {unknown[0]}"})
        with transaction.atomic():
            UserSkill.objects.filter(user=user).delete()
            UserSkill.objects.bulk_create(
                UserSkill(user=user, skill=catalog[row["skill"]], level=row["level"], order=i)
                for i, row in enumerate(rows)
            )
        return self.get(request)


class MyTechnologiesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Texnologiyalar ro'yxati", responses={200: None})
    def get(self, request: Request) -> Response:
        slugs = UserTechnology.objects.filter(user=_me(request)).values_list("slug", flat=True)
        return Response([{"slug": s, "name": TECHNOLOGIES.get(s, s)} for s in slugs])

    @extend_schema(
        summary="Texnologiyalarni almashtirish",
        request={"application/json": {"type": "array", "items": {"type": "string"}}},
        responses={200: None},
    )
    def put(self, request: Request) -> Response:
        user = _me(request)
        slugs = _list_body(request)
        if not all(isinstance(s, str) and s in TECHNOLOGIES for s in slugs):
            raise exceptions.ValidationError({"detail": "Noma'lum texnologiya"})
        if len(set(slugs)) != len(slugs):
            raise exceptions.ValidationError({"detail": "Texnologiya takrorlangan"})
        with transaction.atomic():
            UserTechnology.objects.filter(user=user).delete()
            UserTechnology.objects.bulk_create(
                UserTechnology(user=user, slug=slug, order=i) for i, slug in enumerate(slugs)
            )
        return self.get(request)


class _CareerView(APIView):
    """Ta'lim va ish tajribasi — bir xil «butun ro'yxatni almashtirish» qoidasi."""

    permission_classes = [IsAuthenticated]
    model: Any
    serializer_class: Any

    def get(self, request: Request) -> Response:
        rows = self.model.objects.filter(user=_me(request))
        return Response(self.serializer_class(rows, many=True).data)

    def put(self, request: Request) -> Response:
        user = _me(request)
        serializer = self.serializer_class(data=_list_body(request), many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.model.objects.filter(user=user).delete()
            for i, row in enumerate(serializer.validated_data):
                self.model.objects.create(user=user, order=i, **row)
        return self.get(request)


@extend_schema(
    request=EducationSerializer(many=True), responses={200: EducationSerializer(many=True)}
)
@extend_schema_view(
    get=extend_schema(summary="Ta'lim tarixi"),
    put=extend_schema(summary="Ta'lim tarixini almashtirish"),
)
class MyEducationsView(_CareerView):
    model = Education
    serializer_class = EducationSerializer


@extend_schema(request=WorkSerializer(many=True), responses={200: WorkSerializer(many=True)})
@extend_schema_view(
    get=extend_schema(summary="Ish tajribasi"),
    put=extend_schema(summary="Ish tajribasini almashtirish"),
)
class MyWorkView(_CareerView):
    model = WorkExperience
    serializer_class = WorkSerializer


class MyExternalView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Tashqi profillar", responses={200: ExternalOutSerializer(many=True)})
    def get(self, request: Request) -> Response:
        rows = ExternalProfile.objects.filter(user=_me(request))
        return Response(ExternalOutSerializer(rows, many=True).data)

    @extend_schema(
        summary="Tashqi profillarni almashtirish",
        request=ExternalInSerializer(many=True),
        responses={200: ExternalOutSerializer(many=True)},
    )
    def put(self, request: Request) -> Response:
        user = _me(request)
        serializer = ExternalInSerializer(data=_list_body(request), many=True)
        serializer.is_valid(raise_exception=True)
        rows: list[dict[str, Any]] = serializer.validated_data
        kinds = [row["kind"] for row in rows]
        if len(set(kinds)) != len(kinds):
            raise exceptions.ValidationError({"detail": "Har platformadan bittadan"})
        with transaction.atomic():
            existing = {p.kind: p for p in ExternalProfile.objects.filter(user=user)}
            for row in rows:
                current = existing.get(row["kind"])
                # Handle o'zgarmagan bo'lsa keshlangan reyting saqlanadi —
                # har «Saqlash» Codeforces'ga qayta so'rov bo'lmasin.
                if current is not None and current.handle == row["handle"]:
                    continue
                if current is None:
                    current = ExternalProfile.objects.create(user=user, **row)
                else:
                    current.handle = row["handle"]
                    current.rating = current.max_rating = None
                    current.rank = ""
                    current.fetched_at = None
                    current.save()
                if current.kind in external.FETCHERS:
                    transaction.on_commit(partial(queue, refresh_external, current.pk))
            ExternalProfile.objects.filter(user=user).exclude(kind__in=kinds).delete()
        return self.get(request)


# ── Ommaviy profil ───────────────────────────────────────────────────


class PublicProfileView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Ommaviy profil", responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        viewer = request.user if isinstance(request.user, User) else None
        return Response(public.build_profile(_profile_owner(username), viewer))


class ActivityView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Faollik tarixi",
        parameters=[OpenApiParameter("before", str)],
        responses={200: None},
    )
    def get(self, request: Request, username: str) -> Response:
        before = parse_datetime(request.query_params.get("before", "") or "")
        return Response(public.activity(_profile_owner(username), before=before))


class AchievementsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Yutuqlar", responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        return Response(achievements.rows(_profile_owner(username)))


class PurchasesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Xaridlar tarixi", responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        return Response(public.purchases(_profile_owner(username)))


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def _state(self, target: User, viewer: User) -> Response:
        return Response(
            {
                "followers": Follow.objects.filter(following=target).count(),
                "is_following": Follow.objects.filter(follower=viewer, following=target).exists(),
            }
        )

    @extend_schema(summary="Kuzatish", request=None, responses={200: None})
    def post(self, request: Request, username: str) -> Response:
        viewer, target = _me(request), _profile_owner(username)
        if target.pk == viewer.pk:
            raise exceptions.ValidationError({"detail": "O'zingizni kuzatib bo'lmaydi"})
        Follow.objects.get_or_create(follower=viewer, following=target)
        return self._state(target, viewer)

    @extend_schema(summary="Kuzatishni bekor qilish", responses={200: None})
    def delete(self, request: Request, username: str) -> Response:
        viewer, target = _me(request), _profile_owner(username)
        Follow.objects.filter(follower=viewer, following=target).delete()
        return self._state(target, viewer)


@extend_schema_view(
    get=extend_schema(summary="Obunachilar va obunalar ro'yxati"),
)
class FollowListView(generics.ListAPIView[User]):
    """Obunachilar yoki kuzatilayotganlar — `direction` bilan, qidiruv va saralash."""

    permission_classes = [AllowAny]
    serializer_class = FollowerSerializer
    pagination_class = StandardPagination
    direction = "followers"

    @extend_schema(
        parameters=[
            OpenApiParameter("q", str),
            OpenApiParameter("ordering", str, enum=["recent", "rating", "name"]),
        ]
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[User]:
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()
        owner = _profile_owner(self.kwargs["username"])
        if self.direction == "followers":
            queryset = User.objects.filter(following_links__following=owner, is_active=True)
            recent = "-following_links__created_at"
        else:
            queryset = User.objects.filter(follower_links__follower=owner, is_active=True)
            recent = "-follower_links__created_at"
        q = self.request.query_params.get("q", "").strip()
        if q:
            queryset = queryset.filter(Q(username__icontains=q) | Q(display_name__icontains=q))
        # One stored column instead of a subquery over sessions per row (ADR-0024).
        queryset = queryset.select_related("school_ref").annotate(last_seen=F("last_seen_at"))
        ordering = {"rating": ("-rating_contest", "username"), "name": ("username",)}
        return queryset.order_by(
            *ordering.get(self.request.query_params.get("ordering", ""), (recent,))
        )


@extend_schema(summary="Ulangan ijtimoiy hisoblar")
class MyConnectedView(APIView):
    """Ulangan hisobdagi taxallus — Telegram va GitHub havolasini bir bosishda to'ldirish."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: None})
    def get(self, request: Request) -> Response:
        return Response(external.connected_handles(_me(request)))


# ── Jamoalar ─────────────────────────────────────────────────────────


def _team_error(exc: teams.TeamError) -> exceptions.APIException:
    if isinstance(exc, teams.TeamForbidden):
        return exceptions.PermissionDenied(str(exc))
    return exceptions.ValidationError({"team": str(exc)})


def _team_payload(team: Team, viewer: User) -> dict[str, Any]:
    fresh = Team.objects.prefetch_related("members__user").get(pk=team.pk)
    return dict(TeamSerializer(fresh, context={"viewer": viewer}).data)


class MyTeamsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Mening jamoalarim", responses={200: TeamSerializer(many=True)})
    def get(self, request: Request) -> Response:
        user = _me(request)
        rows = Team.objects.filter(members__user=user).prefetch_related("members__user").distinct()
        return Response(TeamSerializer(rows, many=True, context={"viewer": user}).data)

    @extend_schema(
        summary="Jamoa yaratish", request=TeamCreateSerializer, responses={201: TeamSerializer}
    )
    def post(self, request: Request) -> Response:
        user = _me(request)
        serializer = TeamCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            team = teams.create(user, serializer.validated_data["name"])
        except teams.TeamError as exc:
            raise _team_error(exc) from None
        return Response(_team_payload(team, user), status=status.HTTP_201_CREATED)


class TeamJoinView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Jamoaga qo'shilish", request=TeamJoinSerializer, responses={200: TeamSerializer}
    )
    def post(self, request: Request) -> Response:
        user = _me(request)
        serializer = TeamJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            team = teams.join(user, serializer.validated_data["code"])
        except teams.TeamError as exc:
            raise _team_error(exc) from None
        return Response(_team_payload(team, user))


class TeamDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Jamoani o'chirish", responses={204: None})
    def delete(self, request: Request, pk: int) -> Response:
        try:
            teams.delete(get_object_or_404(Team, pk=pk), _me(request))
        except teams.TeamError as exc:
            raise _team_error(exc) from None
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Taklif kodini yangilash", request=None, responses={200: TeamSerializer})
    def post(self, request: Request, pk: int) -> Response:
        user = _me(request)
        try:
            team = teams.refresh_code(get_object_or_404(Team, pk=pk), user)
        except teams.TeamError as exc:
            raise _team_error(exc) from None
        return Response(_team_payload(team, user))


class TeamLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Jamoadan chiqish", request=None, responses={204: None})
    def post(self, request: Request, pk: int) -> Response:
        try:
            teams.leave(get_object_or_404(Team, pk=pk), _me(request))
        except teams.TeamError as exc:
            raise _team_error(exc) from None
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamMemberView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="A'zoni jamoadan chiqarish", responses={204: None})
    def delete(self, request: Request, pk: int, username: str) -> Response:
        try:
            teams.remove(get_object_or_404(Team, pk=pk), _me(request), username)
        except teams.TeamError as exc:
            raise _team_error(exc) from None
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Profil statistikasi ──────────────────────────────────────────────


@extend_schema(summary="Profil statistikasi")
class UserStatsView(APIView):
    """Yechilgan/jami, daraja kesimi, tillar va verdiktlar ulushi."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        user = _profile_owner(username)
        return Response(stats.cached(user.pk, "overview", lambda: stats.overview(user)))


@extend_schema(summary="Foydalanuvchi kalendari")
class UserCalendarView(APIView):
    """Faollik xaritasi — kunlik urinishlar va yechimlar, streak bilan."""

    permission_classes = [AllowAny]

    @extend_schema(parameters=[OpenApiParameter("year", int)], responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        user = _profile_owner(username)
        this_year = timezone.localdate().year
        raw = request.query_params.get("year") or str(this_year)
        if not raw.isdigit() or not 2000 <= int(raw) <= this_year:
            raise exceptions.ValidationError({"year": "Yil noto'g'ri"})
        year = int(raw)
        return Response(
            stats.cached(user.pk, f"calendar:{year}", lambda: stats.calendar(user, year))
        )


@extend_schema(summary="Masalalar xaritasi")
class UserProblemMapView(APIView):
    """Arxivdagi har masala: yechilgan, urinilgan yoki tegilmagan."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        return Response(stats.problem_map(_profile_owner(username)))


@extend_schema(summary="Reyting grafigi")
class UserRatingSeriesView(APIView):
    """To'rt reyting tarixi grafik uchun, unvon chegaralari bilan."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        return Response(stats.rating_series(_profile_owner(username)))


@extend_schema(summary="Foydalanuvchi mavzulari")
class UserTopicsView(APIView):
    """Mavzu kesimidagi kuch — `problems/skills/` bilan bitta hisob, lekin ommaviy."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        from problems.views import topic_skills

        user = _profile_owner(username)
        return Response(
            {
                "topics": stats.cached(
                    user.pk, "topics", lambda: topic_skills(*stats.problem_sets(user))
                )
            }
        )


@extend_schema(summary="Foydalanuvchi musobaqalari")
class UserContestsView(APIView):
    """Qatnashgan musobaqalar — faqat ommaviylari."""

    permission_classes = [AllowAny]

    @extend_schema(parameters=[OpenApiParameter("q", str)], responses={200: None})
    def get(self, request: Request, username: str) -> Response:
        user = _profile_owner(username)
        queryset = Standing.objects.filter(user=user, contest__is_public=True).select_related(
            "contest"
        )
        q = request.query_params.get("q", "").strip()
        if q:
            queryset = queryset.filter(contest__title__icontains=q)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(
            queryset.order_by("-contest__start_at", "-pk"), request, view=self
        )
        return paginator.get_paginated_response(stats.contest_rows(user, list(page or [])))
