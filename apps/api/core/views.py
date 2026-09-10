"""Auth va token endpointlari — ADR-0008."""

from __future__ import annotations

import logging
import secrets
from datetime import timedelta
from typing import Any

import redis
from django.conf import settings
from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login, logout
from django.contrib.auth import login as django_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import connection
from django.db.models import Q, QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import exceptions, generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from contests.models import Contest
from core import account, handles, oauth, recovery, verification
from core.cache import cache_get, cache_set
from core.models import ApiToken, SocialAccount, User
from core.pagination import StandardPagination, TimeCursorPagination
from core.serializers import (
    AccountDeleteSerializer,
    ApiTokenCreateSerializer,
    ApiTokenSerializer,
    EmailVerifySerializer,
    LoginSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    SocialLinkSerializer,
    UsernameCheckSerializer,
    UserPublicSerializer,
)
from core.tasks import queue, send_email_verify, send_password_reset
from core.throttling import ResilientScopedRateThrottle
from judging.models import Attempt
from problems.models import Problem

MAX_TOKEN_LIFETIME = timedelta(days=365)

log = logging.getLogger(__name__)

#: `django_login()` `authenticate()` siz chaqirilganda backendni O'ZI
#: topa olmaydi — ijtimoiy kirishda parol tekshirilmaydi, shuning uchun
#: u aniq ko'rsatiladi.
DEFAULT_AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"


class HealthView(APIView):
    """Readiness — 10-operations § deploy va monitoring.

    Bog'liqliklar HAQIQATAN tekshiriladi. Shartsiz `ok` qaytaradigan
    health endpoint yo'qidan yomonroq: DB o'lganda ham load balancer
    trafikni shu instansiyaga yuborishda davom etadi, chaos sinovi esa
    hech narsani o'lchamaydi.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []
    #: Throttle kesh (Redis) ga tayanadi. Health aynan shu bog'liqlik
    #: haqida hisobot beradi, ya'ni unga tayana olmaydi: Redis o'lganda
    #: throttle o'zi 500 bilan yiqilib, hisobotni bermay qo'yardi.
    throttle_classes: list[Any] = []

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Barcha bog'liqliklar javob beradi"),
            503: OpenApiResponse(description="Bog'liqlik yetib bo'lmaydi"),
        }
    )
    def get(self, request: Request) -> Response:
        checks = {"database": _check_database(), "redis": _check_redis()}
        healthy = all(v == "ok" for v in checks.values())
        return Response(
            {"status": "ok" if healthy else "degraded", "checks": checks},
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def _check_database() -> str:
    try:
        connection.ensure_connection()
    except Exception as exc:
        return type(exc).__name__
    return "ok"


def _check_redis() -> str:
    try:
        redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2).ping()
    except Exception as exc:
        return type(exc).__name__
    return "ok"


class PlatformStatsView(APIView):
    """Mehmon bosh sahifasi uchun umumiy raqamlar.

    Urinishlar soni boshqa hech qayerdan olinmaydi: `/attempts/` cursor
    paginatsiyada ishlaydi va `count` qaytarmaydi. Katta jadvalda
    `COUNT(*)` arzon emas, shuning uchun natija keshlanadi — landing
    raqami bir daqiqa eskirsa hech narsa yo'qotilmaydi.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []
    CACHE_S = 60

    @extend_schema(responses={200: OpenApiResponse(description="Platforma statistikasi")})
    def get(self, request: Request) -> Response:
        stats = cache_get("platform-stats")
        if stats is None:
            stats = {
                "users": User.objects.filter(is_active=True).count(),
                "problems": Problem.objects.filter(is_public=True).count(),
                "contests": Contest.objects.filter(is_public=True).count(),
                "attempts": Attempt.objects.count(),
                # Arxivdagi til filtri faqat bir nechta til bo'lganda
                # ko'rsatiladi — bitta variantli tanlov shovqin.
                "statement_locales": sorted(
                    set(
                        Problem.objects.filter(is_public=True).values_list(
                            "statement_locale", flat=True
                        )
                    )
                ),
            }
            cache_set("platform-stats", stats, self.CACHE_S)
        return Response(stats)


class CalendarView(APIView):
    """Barcha tadbirlar bir joyda — musobaqa, arena, chempionat, hakaton.

    Duellar shaxsiy: faqat kirgan foydalanuvchining o'zinikilari.
    """

    permission_classes = [AllowAny]
    DEFAULT_DAYS = 60

    @extend_schema(responses={200: OpenApiResponse(description="Tadbirlar ro'yxati")})
    def get(self, request: Request) -> Response:
        from arena.models import ArenaRound
        from duels.models import Duel
        from hackathons.models import Hackathon
        from tournaments.models import Tournament

        now = timezone.now()
        start = _parse_date(request.query_params.get("from")) or now - timedelta(days=7)
        end = _parse_date(request.query_params.get("to")) or now + timedelta(days=self.DEFAULT_DAYS)

        events: list[dict[str, Any]] = []

        def add(kind: str, slug: str, title: str, start_at: Any, end_at: Any, **extra: Any) -> None:
            events.append(
                {
                    "kind": kind,
                    "slug": slug,
                    "title": title,
                    "start_at": start_at,
                    "end_at": end_at,
                    **extra,
                }
            )

        for c in Contest.objects.filter(is_public=True, start_at__range=(start, end)):
            add("contest", c.slug, c.title, c.start_at, c.end_at, is_rated=c.is_rated)
        for a in ArenaRound.objects.filter(is_public=True, start_at__range=(start, end)):
            add("arena", a.slug, a.title, a.start_at, a.end_at)
        for t in Tournament.objects.filter(is_public=True, start_at__range=(start, end)):
            add("tournament", t.slug, t.title, t.start_at, t.end_at)
        for h in Hackathon.objects.filter(is_public=True, start_at__range=(start, end)):
            add(
                "hackathon",
                h.slug,
                h.title,
                h.start_at,
                h.end_at,
                submission_deadline=h.submission_deadline,
            )
        if isinstance(request.user, User):
            mine = Duel.objects.filter(
                status=Duel.Status.ACCEPTED, start_at__range=(start, end)
            ).filter(Q(challenger=request.user) | Q(opponent=request.user))
            for d in mine:
                add("duel", d.slug, d.title, d.start_at, d.end_at)

        events.sort(key=lambda e: e["start_at"])
        return Response({"from": start, "to": end, "results": events})


def _parse_date(raw: str | None) -> Any:
    if not raw:
        return None
    from django.utils.dateparse import parse_datetime

    parsed = parse_datetime(raw)
    if parsed is not None and timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed


class SearchView(APIView):
    """Header qidiruvi — har turdan bir nechta natija, tez."""

    permission_classes = [AllowAny]
    PER_TYPE = 5

    @extend_schema(responses={200: OpenApiResponse(description="Qidiruv natijalari")})
    def get(self, request: Request) -> Response:
        from content.models import Article
        from problems.models import normalize_search

        q = (request.query_params.get("q") or "").strip()
        if len(q) < 2:
            return Response({"q": q, "problems": [], "users": [], "articles": [], "contests": []})
        n = self.PER_TYPE
        # Masala arxivi allaqachon shunday qidiradi (problems.filters), bu
        # yerda esa xom `title` bo'yicha edi: o'zbek klaviaturasi `ʻ` yoki
        # `’` beradi, baza `'` bilan saqlanadi va «0 ga boʻlish» hech narsa
        # topmasdi — o'lchandi, to'g'ri apostrof bilan 0 natija.
        needle = normalize_search(q)
        return Response(
            {
                "q": q,
                "problems": [
                    {"slug": p.slug, "title": p.title, "difficulty": p.difficulty}
                    for p in Problem.objects.filter(is_public=True, title_search__icontains=needle)[
                        :n
                    ]
                ],
                "users": [
                    {
                        "username": u.username,
                        "display_name": u.display_name,
                        "rating_skills": u.rating_skills,
                    }
                    for u in User.objects.filter(is_active=True).filter(
                        Q(username__icontains=q) | Q(display_name__icontains=q)
                    )[:n]
                ],
                "articles": [
                    {"slug": a.slug, "title": a.title, "kind": a.kind}
                    for a in Article.objects.filter(is_published=True, title__icontains=q)[:n]
                ],
                "contests": [
                    {"slug": c.slug, "title": c.title, "start_at": c.start_at}
                    for c in Contest.objects.filter(is_public=True, title__icontains=q)[:n]
                ],
            }
        )


class RegisterView(generics.CreateAPIView[User]):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    # Hisob ochish botlar uchun eng qulay nishon. CAPTCHA hammaga
    # ko'rsatilmaydi — avval shu chegara ishlaydi.
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "register"

    def perform_create(self, serializer: Any) -> None:
        user = serializer.save()
        # Tasdiqlash YUMSHOQ: xat ketmasa ham hisob ochilgan bo'lib
        # qoladi, shuning uchun bu yerda hech qanday xato ushlanmaydi —
        # `send_email` zanjiri o'zi hech qachon otmaydi.
        issued = verification.issue(user, enforce_limit=False)
        queue(send_email_verify, user.pk, issued.raw, issued.code)


class SocialLinkStartView(APIView):
    """Telegram'ni ulash niyatini belgilaydi.

    Telegram vidjeti `SocialStartView` dan o'tmaydi va uning callback'i
    `state` siz GET — ya'ni «kirgan bo'lsa bog'la» qoidasi hisobni
    egallash yo'li bo'lardi: hujumchi qurbonning brauzerini o'zining
    imzolangan ma'lumoti bilan o'sha manzilga yuborib, o'z Telegramini
    qurbon hisobiga ulab olardi va keyin uning nomidan kirardi.
    Shu sababli niyat SESSIYADA va faqat shu POST orqali qo'yiladi:
    DRF sessiya autentifikatsiyasi POST'ga CSRF tekshiruvini talab
    qiladi, ya'ni begona sayt uni chaqira olmaydi.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request: Request, provider: str) -> Response:
        assert isinstance(request.user, User)
        if provider not in oauth.configured():
            raise exceptions.ValidationError({"provider": "Provayder sozlanmagan"})
        request.session["social_link_for"] = {"user": request.user.pk, "provider": provider}
        return Response(status=status.HTTP_204_NO_CONTENT)


class SocialUnlinkView(APIView):
    """Ulangan hisobni uzadi.

    Yagona kirish yo'lini uzib bo'lmaydi: paroli yo'q va boshqa
    provayderi ham qolmagan odam o'z hisobiga qaytib kira olmasdi.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request: Request, provider: str) -> Response:
        assert isinstance(request.user, User)
        user = request.user
        row = SocialAccount.objects.filter(user=user, provider=provider).first()
        if row is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        others = SocialAccount.objects.filter(user=user).exclude(pk=row.pk).exists()
        if not user.has_usable_password() and not others:
            raise exceptions.ValidationError(
                {"provider": "Bu yagona kirish yo'lingiz — avval parol o'rnating"}
            )
        row.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailVerifyView(APIView):
    """Havola yoki kod bilan pochtani tasdiqlaydi.

    Kirish talab qilinmaydi: havola pochtadan, ko'pincha boshqa
    qurilmadagi brauzerda ochiladi va u yerda sessiya bo'lmaydi.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(request=EmailVerifySerializer, responses={204: None})
    def post(self, request: Request) -> Response:
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = verification.consume(
            raw=serializer.validated_data.get("token", ""),
            code=serializer.validated_data.get("code", ""),
            username=serializer.validated_data.get("username", ""),
        )
        if user is None:
            raise exceptions.ValidationError({"token": "Havola yaroqsiz yoki muddati tugagan"})
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailVerifyResendView(APIView):
    """Xatni qaytadan yuboradi. Faqat o'z hisobiga."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(request=None, responses={204: None})
    def post(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        user = request.user
        if not user.email or user.email_verified_at is not None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            issued = verification.issue(user)
        except verification.TooManyRequests as exc:
            raise exceptions.Throttled(
                detail="Juda ko'p so'rov — birozdan keyin urinib ko'ring"
            ) from exc
        queue(send_email_verify, user.pk, issued.raw, issued.code)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    parameters=[OpenApiParameter("u", str, description="Tekshiriladigan taxallus")],
    responses={200: UsernameCheckSerializer},
)
class UsernameCheckView(APIView):
    """Taxallus bo'shmi — yozayotganda chaqiriladi.

    Bu endpoint nomlarni sanab chiqishga yo'l ochadi. Uni yashirishning
    ma'nosi yo'q: ro'yxatdan o'tishga urinib ham xuddi shu javob olinadi,
    taxalluslar esa standings'da ochiq turadi. Shuning uchun himoya —
    yashirish emas, chegara (`username_check`).
    """

    permission_classes = [AllowAny]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "username_check"

    def get(self, request: Request) -> Response:
        value = request.query_params.get("u", "").strip()
        try:
            handles.validate(value)
        except DjangoValidationError as exc:
            return Response({"available": False, "reason": exc.messages[0]})

        taken = User.objects.filter(username__iexact=value).exists()
        similar = User.objects.filter(username_skeleton=handles.skeleton(value)).exists()
        if taken:
            return Response({"available": False, "reason": "Bu username band"})
        if similar:
            return Response(
                {"available": False, "reason": "Bu username mavjud nomga juda o'xshash"}
            )
        return Response({"available": True, "reason": ""})


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: MeSerializer})
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = django_authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Login yoki parol noto'g'ri",
                        "details": {},
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        return Response(MeSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateDestroyAPIView[User]):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        assert isinstance(self.request.user, User)
        return self.request.user

    def perform_update(self, serializer: Any) -> None:
        user = serializer.save()
        # Profil to'ldirilgan bo'lsa — bir martalik quest (ADR-0002)
        from qvant.quests import on_profile_completed, profile_is_complete

        if profile_is_complete(user):
            on_profile_completed(user)

    @extend_schema(request=AccountDeleteSerializer, responses={204: None})
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Hisobni o'chiradi — anonimlashtirish orqali (`core.account`)."""
        user = self.get_object()
        serializer = AccountDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Parol o'g'irlangan sessiya bilan hisobni yo'q qilishning oldini
        # oladi: qaytarib bo'lmaydigan amal uchun bir marta tasdiq shart.
        if not user.check_password(serializer.validated_data["password"]):
            raise exceptions.ValidationError({"password": "Parol noto'g'ri"})
        account.anonymize(user)
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeExportView(APIView):
    """Foydalanuvchining o'z ma'lumoti — JSON fayl.

    O'chirish qaytarib bo'lmaydi, shuning uchun undan oldin hamma narsani
    olib qolish yo'li bo'lishi kerak. Javob og'ir (ichida yuborilgan
    kodlar bor) — shuning uchun alohida shift.
    """

    permission_classes = [IsAuthenticated]
    # Shift `throttle_scope` orqali ishlashi uchun sinf ATAYIN
    # ko'rsatiladi: u sozlamalardagi standart ro'yxatda yo'q.
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "export"

    @extend_schema(responses={200: OpenApiResponse(description="JSON eksport")})
    def get(self, request: Request) -> Response:
        assert isinstance(request.user, User)
        response = Response(account.export(request.user))
        response["Content-Disposition"] = 'attachment; filename="rankwant-export.json"'
        return response


class UserViewSet(viewsets.ReadOnlyModelViewSet[User]):
    """Ommaviy profil va leaderboard."""

    serializer_class = UserPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = "username"
    queryset = User.objects.filter(is_active=True)
    ordering_fields = ["rating_skills", "rating_contest", "rating_challenges", "date_joined"]
    ordering = ["-rating_skills"]


class RatingHistoryView(generics.ListAPIView[Any]):
    """Reyting o'zgarishlari tarixi — 05-domain-model 🔒.

    Ommaviy: reyting qanday shakllanganini har kim ko'ra olishi kerak
    (principle #2). Sabab, eski va yangi qiymat, contest holatida esa
    seed va rank ham beriladi.
    """

    permission_classes = [AllowAny]
    pagination_class = TimeCursorPagination

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        from ratings.serializers import RatingHistorySerializer

        return RatingHistorySerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        from ratings.models import RatingHistory

        user = get_object_or_404(User, username=self.kwargs["username"], is_active=True)
        qs = RatingHistory.objects.filter(user=user)
        rating_type = self.request.query_params.get("type")
        if rating_type:
            qs = qs.filter(rating_type=rating_type)
        return qs


class SolvedProblemsView(generics.ListAPIView[Any]):
    """Foydalanuvchi yechgan masalalar — Skills reytingining manbai."""

    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        from ratings.serializers import SolvedProblemSerializer

        return SolvedProblemSerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        from ratings.models import UserSolvedProblem

        user = get_object_or_404(User, username=self.kwargs["username"], is_active=True)
        return (
            UserSolvedProblem.objects.filter(user=user)
            .select_related("problem")
            .order_by("-problem__difficulty")
        )


class ApiTokenViewSet(viewsets.ModelViewSet[ApiToken]):
    """PAT boshqaruvi. Ochiq token FAQAT yaratilganda qaytariladi."""

    serializer_class = ApiTokenSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self) -> QuerySet[ApiToken]:
        assert isinstance(self.request.user, User)
        return ApiToken.objects.filter(user=self.request.user).order_by("-created_at")

    @extend_schema(request=ApiTokenCreateSerializer, responses={201: ApiTokenSerializer})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(request.user, User)
        user = request.user

        serializer = ApiTokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        active = ApiToken.objects.filter(user=user, revoked_at__isnull=True).count()
        if active >= ApiToken.MAX_ACTIVE_PER_USER:
            return Response(
                {
                    "error": {
                        "code": "token_limit",
                        "message": f"Maksimal {ApiToken.MAX_ACTIVE_PER_USER} ta faol token",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        expires_at = data["expires_at"]
        if expires_at <= timezone.now():
            return Response(
                {
                    "error": {
                        "code": "invalid_expiry",
                        "message": "Muddat kelajakda bo'lishi kerak",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if expires_at > timezone.now() + MAX_TOKEN_LIFETIME:
            return Response(
                {
                    "error": {
                        "code": "invalid_expiry",
                        "message": "Maksimal muddat — 1 yil",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, raw = ApiToken.issue(user, data["name"], data["scopes"], expires_at)
        payload = ApiTokenSerializer(token).data
        # Ochiq token faqat SHU YERDA, bir marta.
        payload["token"] = raw
        return Response(payload, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance: ApiToken) -> None:
        # O'chirmaymiz — bekor qilamiz. Audit izi saqlanadi.
        instance.revoked_at = timezone.now()
        instance.save(update_fields=["revoked_at"])


class PasswordResetRequestView(APIView):
    """Tiklash xatini so'raydi (ADR-0015).

    HAR DOIM 202 qaytaradi — hisob bor-yo'qligidan qat'i nazar. Aks holda
    bu endpoint hisob mavjudligini tekshirish quroli bo'lardi: kimdir
    manzillar ro'yxatini yuborib, qaysilari ro'yxatdan o'tganini bilib olardi.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(request=PasswordResetRequestSerializer, responses={202: None})
    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login = serializer.validated_data["login"].strip()

        user = User.objects.filter(
            Q(username__iexact=login) | Q(email__iexact=login), is_active=True
        ).first()
        if user is not None and user.email:
            ident = ResilientScopedRateThrottle().get_ident(request)
            try:
                issued = recovery.issue(
                    user, ip=ident, user_agent=request.META.get("HTTP_USER_AGENT", "")
                )
            except recovery.TooManyRequests:
                # Chegaraga urilgani ham SIR: javob baribir bir xil.
                log.info("tiklash chegarasi: %s", user.pk)
            else:
                send_password_reset.delay(
                    user.pk,
                    issued.raw,
                    issued.code,
                    issued.row.request_ip or "",
                    issued.row.request_ua,
                )
        return Response(status=status.HTTP_202_ACCEPTED)


class PasswordResetConfirmView(APIView):
    """Havola yoki kod bilan yangi parol o'rnatadi."""

    permission_classes = [AllowAny]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(request=PasswordResetConfirmSerializer, responses={204: None})
    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Avval EGASINI aniqlaymiz, tokenni yoqmasdan: yangi parol
        # qoidaga to'g'ri kelmasa havola omon qolishi kerak.
        lookup = {
            "raw": data.get("token", ""),
            "code": data.get("code", ""),
            "username": data.get("username", ""),
        }
        user = recovery.consume(**lookup, commit=False)
        if user is None:
            return Response(
                {
                    "error": {
                        "code": "invalid_token",
                        "message": "Havola yaroqsiz yoki muddati tugagan",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parol endi tekshiriladi: foydalanuvchi ma'lum, ya'ni
        # `UserAttributeSimilarityValidator` ham ishlaydi.
        try:
            validate_password(data["password"], user)
        except DjangoValidationError as exc:
            return Response(
                {"error": {"code": "invalid", "message": " ".join(exc.messages), "details": {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parol o'tdi — endi tokenni yoqamiz. Shu bir zumda boshqa so'rov
        # uni ishlatib ulgurgan bo'lishi mumkin, shuning uchun natija
        # tekshiriladi.
        if recovery.consume(**lookup) is None:
            return Response(
                {
                    "error": {
                        "code": "invalid_token",
                        "message": "Havola yaroqsiz yoki muddati tugagan",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(data["password"])
        user.save(update_fields=["password"])
        # Eski sessiyalar qoladi-yu, parol o'zgargani uchun ular
        # `AbstractBaseUser.get_session_auth_hash()` bilan bekor bo'ladi.
        log.info("parol tiklandi: %s", user.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthProvidersView(APIView):
    """Sozlangan ijtimoiy kirish provayderlari.

    Frontend shu ro'yxat bo'yicha tugma chizadi: kaliti yo'q provayder
    tugmasi umuman ko'rinmaydi va foydalanuvchi ishlamaydigan yo'lni
    bosmaydi (ADR-0016).
    """

    permission_classes = [AllowAny]

    @extend_schema(responses={200: None})
    def get(self, request: Request) -> Response:
        return Response(
            {
                "providers": oauth.configured(),
                # Telegram widgetiga bot nomi kerak — u sir emas.
                "telegram_bot": settings.TELEGRAM_BOT_USERNAME,
            }
        )


#: Bog'lash tokeni sessiyada shuncha turadi. Foydalanuvchi parolini
#: kiritishga ulguradigan, lekin ochiq qolib ketmaydigan muddat.
SOCIAL_LINK_TTL = 600


class SocialStartView(APIView):
    """Provayderning ruxsat sahifasiga yo'naltiradi."""

    permission_classes = [AllowAny]

    @extend_schema(responses={302: None})
    def get(self, request: Request, provider: str) -> HttpResponseRedirect:
        if provider not in oauth.configured() or provider not in oauth.AUTHORIZE:
            # Telegram bu yerga TUSHMAYDI: u OAuth emas va frontend uning
            # o'z widgetini chizadi. Shunga qaramay tekshiruv turadi —
            # aks holda bu yo'l 500 berardi.
            return redirect(f"{settings.SITE_URL}/login?social=unavailable")
        state = oauth.new_state()
        # CSRF: qaytgan `state` sessiyadagisi bilan solishtiriladi, ya'ni
        # begona sayt bizning callback'imizga o'z kodini yubora olmaydi.
        request.session["social_state"] = state
        request.session["social_provider"] = provider
        # Kirgan odam uchun bu KIRISH emas, BOG'LASH: qaytganda yangi
        # hisob ochilmasligi va parol so'ralmasligi kerak — u allaqachon
        # o'zini isbotlagan. Pochta mosligiga tayanmaydi, ya'ni ish
        # pochtasini shaxsiy hisobga ulash ham mumkin.
        if request.user.is_authenticated:
            request.session["social_link_for"] = {
                "user": request.user.pk,
                "provider": provider,
            }
        else:
            request.session.pop("social_link_for", None)
        return redirect(oauth.authorize_url(provider, state))


class SocialCallbackView(APIView):
    """Kodni almashtiradi va hisobni topadi yoki yaratadi."""

    permission_classes = [AllowAny]

    @extend_schema(responses={302: None})
    def get(self, request: Request, provider: str) -> HttpResponseRedirect:
        home = settings.SITE_URL
        if provider not in oauth.configured():
            return redirect(f"{home}/login?social=unavailable")
        # BO'SHLIK tekshiruvi ataylab alohida: `None != None` yolg'on
        # bo'lgani uchun, `state` siz kelgan so'rov ochiq oqimi yo'q
        # brauzerda tekshiruvdan O'TIB KETARDI — hujumchi qurbonni o'z
        # hisobiga kiritib qo'yishi mumkin edi (login CSRF).
        state = request.GET.get("state", "")
        expected = request.session.pop("social_state", "") or ""
        if not state or not expected or not secrets.compare_digest(state, expected):
            log.warning("social state mos kelmadi: %s", provider)
            return redirect(f"{home}/login?social=error")

        try:
            ident = oauth.identity(provider, request.GET.get("code", ""))
        except oauth.OAuthError:
            log.exception("social almashuv yiqildi: %s", provider)
            return redirect(f"{home}/login?social=error")

        return self._finish(request, ident)

    def _finish(self, request: Request, ident: oauth.Identity) -> HttpResponseRedirect:
        home = settings.SITE_URL
        if not ident.uid:
            return redirect(f"{home}/login?social=error")

        link = SocialAccount.objects.filter(provider=ident.provider, uid=ident.uid).first()

        intent = request.session.pop("social_link_for", None)
        if isinstance(intent, dict) and intent.get("provider") == ident.provider:
            owner_pk = intent.get("user")
            owner = (
                User.objects.filter(pk=owner_pk, is_active=True).first()
                if isinstance(owner_pk, int)
                else None
            )
            if owner is None:
                return redirect(f"{home}/settings?social=error")
            if link is not None and link.user_id != owner.pk:
                # Bitta provayder hisobi ikki joyda tura olmaydi —
                # modeldagi `uniq_social_uid` shuni talab qiladi.
                return redirect(f"{home}/settings?social=taken")
            SocialAccount.objects.update_or_create(
                user=owner,
                provider=ident.provider,
                defaults={"uid": ident.uid, "email": ident.email},
            )
            if owner.email_verified_at is None and ident.email.lower() == owner.email.lower():
                owner.email_verified_at = timezone.now()
                owner.save(update_fields=["email_verified_at"])
            return redirect(f"{home}/settings?social=linked")

        if link is not None:
            django_login(request, link.user, backend=DEFAULT_AUTH_BACKEND)
            return redirect(f"{home}/")

        existing = User.objects.filter(email__iexact=ident.email).first() if ident.email else None
        if existing is not None:
            # ADR-0016: avtomatik bog'lash hisobni egallash yo'li bo'lardi,
            # chunki emailni tasdiqlash majburiy emas.
            request.session["social_pending"] = {
                "provider": ident.provider,
                "uid": ident.uid,
                "email": ident.email,
                "user": existing.pk,
                "at": timezone.now().isoformat(),
            }
            return redirect(f"{home}/login?link={ident.provider}")

        user = User.objects.create_user(
            username=oauth.free_username(ident.suggested),
            email=ident.email,
            # Provayder bergan pochta ALLAQACHON tasdiqlangan: `oauth`
            # moduli Google'dan `email_verified` bo'lmasa, GitHub'dan esa
            # `primary and verified` bo'lmasa manzilni umuman olmaydi.
            # Ustidan yana o'z xatimizni yuborish bizdan kuchliroq tomon
            # tekshirgan narsani qayta so'rash bo'lardi — va o'lchandi:
            # usiz hisobda «pochtangiz tasdiqlanmagan» banneri turardi.
            email_verified_at=timezone.now() if ident.email else None,
            locale=request.LANGUAGE_CODE[:2] if hasattr(request, "LANGUAGE_CODE") else "uz",
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])
        SocialAccount.objects.create(
            user=user, provider=ident.provider, uid=ident.uid, email=ident.email
        )
        django_login(request, user, backend=DEFAULT_AUTH_BACKEND)
        return redirect(f"{home}/")


class SocialTelegramView(SocialCallbackView):
    """Telegram widget imzolangan ma'lumotni to'g'ridan-to'g'ri yuboradi —
    kod almashuvi yo'q."""

    @extend_schema(responses={302: None})
    def get(self, request: Request, provider: str = "telegram") -> HttpResponseRedirect:
        home = settings.SITE_URL
        if "telegram" not in oauth.configured():
            return redirect(f"{home}/login?social=unavailable")
        try:
            ident = oauth.telegram_identity(request.GET.dict())
        except oauth.OAuthError:
            log.warning("telegram imzosi rad etildi")
            return redirect(f"{home}/login?social=error")
        return self._finish(request, ident)


class SocialLinkView(APIView):
    """Parol bilan tasdiqlab, ijtimoiy hisobni mavjud hisobga bog'laydi."""

    permission_classes = [AllowAny]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(request=SocialLinkSerializer, responses={204: None})
    def post(self, request: Request) -> Response:
        serializer = SocialLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pending = request.session.get("social_pending")

        def refuse() -> Response:
            return Response(
                {
                    "error": {
                        "code": "invalid_link",
                        "message": "Bog'lash so'rovi topilmadi yoki muddati tugagan",
                        "details": {},
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pending:
            return refuse()
        started = parse_datetime(pending.get("at", "")) or timezone.now()
        if (timezone.now() - started).total_seconds() > SOCIAL_LINK_TTL:
            request.session.pop("social_pending", None)
            return refuse()

        user = User.objects.filter(pk=pending["user"], is_active=True).first()
        if user is None or not user.check_password(serializer.validated_data["password"]):
            # Parol xato — so'rov saqlanadi, foydalanuvchi qayta urinsin.
            return refuse()

        request.session.pop("social_pending", None)
        SocialAccount.objects.get_or_create(
            user=user,
            provider=pending["provider"],
            defaults={"uid": pending["uid"], "email": pending["email"]},
        )
        # Ikki isbot ham qo'lda: provayder manzilni tasdiqlagan va
        # foydalanuvchi hisob parolini bildi. Bundan ortiq tasdiq
        # so'rashning ma'nosi yo'q.
        if user.email_verified_at is None and pending["email"].lower() == user.email.lower():
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at"])
        django_login(request, user, backend=DEFAULT_AUTH_BACKEND)
        return Response(status=status.HTTP_204_NO_CONTENT)
