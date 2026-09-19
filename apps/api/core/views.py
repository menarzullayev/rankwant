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
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import exceptions, generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from contests.models import Contest
from core import account, handles, oauth, recovery, usernames, verification
from core.cache import cache_get, cache_set
from core.models import (
    AnalyticsEvent,
    ApiToken,
    SiteAppearance,
    SocialAccount,
    User,
    UsernameHistory,
)
from core.openapi_docs import crud_summaries
from core.pagination import StandardPagination, TimeCursorPagination
from core.serializers import (
    AccountDeleteSerializer,
    AnalyticsBatchSerializer,
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


@extend_schema(summary="Xizmat holati")
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


def _judge_queue_len() -> int | None:
    """Judge Redis navbati — readiness emas, SLO signal."""
    try:
        return int(
            redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2).llen(
                settings.JUDGE_JOBS_KEY
            )
        )
    except Exception:
        return None


@extend_schema(summary="Sig'im signallari")
class SloView(APIView):
    """Kuzatuv. Load balancer bunisi bilan instansiyani chiqarmaydi.

    `HealthView` DB/Redis o'lganda 503. Bu yerda navbat uzunligi
    axborot: 50k / contest oldidan judge host qo'shish uchun.
    Sentry yo'q (2026-09-19 qaror).
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []
    throttle_classes: list[Any] = []

    @extend_schema(responses={200: OpenApiResponse(description="Judge navbati va bog'liqliklar")})
    def get(self, request: Request) -> Response:
        return Response(
            {
                "judge_queue": _judge_queue_len(),
                "checks": {"database": _check_database(), "redis": _check_redis()},
            }
        )


@extend_schema(summary="Platforma statistikasi")
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


@extend_schema(summary="Faoliyat kalendari")
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


@extend_schema(summary="Global qidiruv")
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


@extend_schema_view(post=extend_schema(summary="Ro'yxatdan o'tish"))
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


@extend_schema(summary="Ijtimoiy hisobni uzish")
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
                {"provider": "This is your only sign-in method — set a password first"}
            )
        row.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(summary="Email'ni kod bilan tasdiqlash")
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
            raise exceptions.ValidationError({"token": "This link is invalid or has expired"})
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(summary="Tasdiqlash kodini qayta yuborish")
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
                detail="Too many requests — try again shortly"
            ) from exc
        queue(send_email_verify, user.pk, issued.raw, issued.code)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    parameters=[OpenApiParameter("u", str, description="Tekshiriladigan taxallus")],
    responses={200: UsernameCheckSerializer},
)
@extend_schema(summary="Username band emasligini tekshirish")
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
            return Response({"available": False, "reason": "This username is taken"})
        if similar:
            return Response(
                {"available": False, "reason": "This username is too similar to an existing one"}
            )
        from core.usernames import reserved

        if reserved(value):
            return Response(
                {
                    "available": False,
                    "reason": "This name recently belonged to another user",
                }
            )
        return Response({"available": True, "reason": ""})


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="Tizimga kirish", request=LoginSerializer, responses={200: MeSerializer})
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Qiymat foydalanuvchi nomi YOKI email bo'lishi mumkin (4-qaror):
        # qaysi ustun ekanini PARSING qilmaymiz — backend ikkalasini bir
        # so'rovda tekshiradi. `@` belgisiga qarab shoxlash xato
        # bo'lardi: email'da `@` bo'lmasligi ham mumkin va nomda ham
        # uchraydi (masalan `ali@2007`).
        user = django_authenticate(
            request,
            username=serializer.validated_data["identifier"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            # Matn ikkala holatda BIR XIL: «bunday hisob yo'q» va «parol
            # noto'g'ri» ni ajratib ko'rsatish mavjud nomlarni sanab
            # chiqish yo'li bo'lardi (ADR-0015).
            return Response(
                {
                    "error": {
                        "code": "invalid_credentials",
                        "message": "Wrong username or password",
                        "details": {},
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        # «Meni eslab qol» (qaror 7): belgilansa sessiya 30 kun yashaydi,
        # belgilanmasa `0` — brauzer yopilganda tugaydi. `set_expiry`
        # `login()` dan KEYIN chaqirilishi shart: `login()` sessiyani
        # almashtiradi va avval qo'yilgan muddatni tashlab yuboradi.
        request.session.set_expiry(
            settings.SESSION_COOKIE_AGE if serializer.validated_data.get("remember") else 0
        )
        return Response(MeSerializer(user).data)


@extend_schema(summary="Analitika hodisasini qabul qilish")
class AnalyticsEventView(APIView):
    """Funnel hodisalarini qabul qiladi (qaror 17).

    `AllowAny` — ATAYIN: eng qimmatli ma'lumot ro'yxatdan O'TMAGAN
    odamdan keladi (qaysi maydonda ketdi), ya'ni kirish talab qilinsa
    funnel umuman ko'rinmasdi. Throttle esa bazani to'ldirishga yo'l
    qo'ymaydi.

    IP saqlanmaydi: u shaxsiy ma'lumot, funnel uchun esa kerak emas.
    Sessiya kaliti bog'lanish uchun yetarli.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ResilientScopedRateThrottle]
    throttle_scope = "analytics"

    @extend_schema(request=AnalyticsBatchSerializer, responses={204: None})
    def post(self, request: Request) -> Response:
        serializer = AnalyticsBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ""
        locale = request.COOKIES.get("rw_locale", "")

        # `bulk_create` — bitta INSERT, ya'ni 25 ta hodisa ham bir
        # so'rovda yoziladi. Funnel yozuvi foydalanuvchini kutdirmasligi
        # kerak, shuning uchun javob `204` va tana yo'q.
        AnalyticsEvent.objects.bulk_create(
            [
                AnalyticsEvent(
                    name=event["name"],
                    user=user,
                    session_key=session_key,
                    path=event.get("path", ""),
                    locale=locale,
                    props=event.get("props") or {},
                )
                for event in serializer.validated_data["events"]
            ]
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Tizimdan chiqish", request=None, responses={204: None})
    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(summary="O'z profili"),
    put=extend_schema(summary="Profilni to'liq yangilash"),
    patch=extend_schema(summary="Profilni qisman yangilash"),
    delete=extend_schema(summary="Hisobni o'chirish (anonimlashtirish)"),
)
class MeView(generics.RetrieveUpdateDestroyAPIView[User]):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # CSRF cookie faqat login paytida qo'yiladi. U yo'qolib, sessiya tirik
        # qolsa, har saqlash 403 bo'lardi — web har yuklanishda shu so'rovni
        # yuboradi, ya'ni cookie shu yerda qaytadi.
        return super().get(request, *args, **kwargs)

    def get_object(self) -> User:
        assert isinstance(self.request.user, User)
        return self.request.user

    def perform_update(self, serializer: Any) -> None:
        # Foydalanuvchi nomi -- ALOHIDA yo'l. `serializer.save()` uni
        # to'g'ridan-to'g'ri yozardi, natijada:
        #   1) bepul almashtirish imkoniyati sarflanmasdan nom o'zgarardi
        #      (`username_changed_at` yangilanmasdan qolardi), ya'ni
        #      cheklov umuman ishlamasdi;
        #   2) `UsernameHistory` yozilmasdi -- eski profil havolasi
        #      yo'naltirmasdi va `usernames.reserved` eski nomni
        #      90 kun band qilmasdi.
        # Endi ikki holat ajratiladi: VAQTINCHALIK nom (ro'yxatdan
        # o'tishning 2-qadami, `u` bilan boshlanadi) -- `claim_temp`;
        # qolgani -- `change` (narx va 90 kunlik bandlik bilan).
        assert isinstance(self.request.user, User)
        wanted = serializer.validated_data.get("username")
        if wanted and wanted != self.request.user.username:
            try:
                if usernames.is_temp_username(self.request.user.username):
                    usernames.claim_temp(self.request.user, wanted)
                else:
                    usernames.change(self.request.user, wanted)
            except usernames.ChangeError as exc:
                # `ChangeError.code` API shartnomasiga o'giriladi:
                # DRF xatosi maydonga bog'lanadi va frontend uni
                # maydon tagida ko'rsatadi.
                raise exceptions.ValidationError({"username": str(exc)}) from exc
            serializer.validated_data.pop("username", None)

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
            raise exceptions.ValidationError({"password": "Password is wrong"})
        account.anonymize(user)
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(summary="Profil ma'lumotlarini eksport qilish (JSON)")
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


@crud_summaries(one="foydalanuvchi", many="foydalanuvchilar", only=("list", "retrieve"))
class UserViewSet(viewsets.ReadOnlyModelViewSet[User]):
    """Ommaviy profil va leaderboard."""

    serializer_class = UserPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = "username"
    #: Taxallusda nuqta bo'lishi mumkin (`ali.valiyev`) — router'ning
    #: standart `[^/.]+` qolipi uni kesib, profilni 404 qilardi.
    lookup_value_regex = "[^/]+"
    queryset = User.objects.filter(is_active=True)
    #: `solved_count` is a stored column since ADR-0024, so sorting by it is an index scan.
    ordering_fields = [
        "rating_skills",
        "rating_contest",
        "rating_challenges",
        "solved_count",
        "date_joined",
    ]
    # `-pk` — tiebreaker: reyting teng bo'lganda tartib aks holda SQL
    # ixtiyoriga qoladi va sahifalash beqaror bo'ladi (bir odam ikki
    # sahifada chiqishi yoki umuman ko'rinmasligi mumkin).
    ordering = ["-rating_skills", "-pk"]

    def get_queryset(self) -> QuerySet[User]:
        queryset = super().get_queryset()
        # Maktab reytingi va sinfdoshlar — katalogdagi maktab bo'yicha.
        school = self.request.query_params.get("school", "")
        if school.isdigit():
            queryset = queryset.filter(school_ref_id=int(school))
        return queryset

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            moved = (
                UsernameHistory.objects.filter(
                    old_username__iexact=kwargs.get("username", ""), user__is_active=True
                )
                .select_related("user")
                .order_by("-changed_at")
                .first()
            )
            if moved is None:
                raise
            # Eski nom: javobdagi `username` yangisi — frontend unga
            # yo'naltiradi, ya'ni eski havolalar ishlashda davom etadi.
            return Response(self.get_serializer(moved.user).data)


@extend_schema(summary="Reyting tarixi")
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


def _best_accepted(rows: list[Any]) -> dict[int, dict[str, Any]]:
    """Har yechilgan masala uchun eng yaxshi vaqt, xotira va AC olgan tillar.

    Faqat joriy sahifadagi masalalar uchun bitta so'rov — sahifada 25 ta
    masala bo'lsa ham, 25 ta so'rov emas.
    """
    from judging.verdicts import Verdict

    if not rows:
        return {}
    best: dict[int, dict[str, Any]] = {}
    for problem_id, language, time_ms, memory_kb in (
        Attempt.objects.filter(
            user_id=rows[0].user_id,
            problem_id__in=[row.problem_id for row in rows],
            verdict=Verdict.AC,
        )
        .order_by("created_at")
        .values_list("problem_id", "language__code", "time_ms", "memory_kb")
    ):
        entry = best.setdefault(
            problem_id, {"time_ms": time_ms, "memory_kb": memory_kb, "languages": []}
        )
        entry["time_ms"] = min(entry["time_ms"], time_ms)
        entry["memory_kb"] = min(entry["memory_kb"], memory_kb)
        if language not in entry["languages"]:
            entry["languages"].append(language)
    return best


@extend_schema(summary="Yechilgan masalalar")
class SolvedProblemsView(generics.ListAPIView[Any]):
    """Foydalanuvchi yechgan masalalar — Skills reytingining manbai.

    `?q=` — nom yoki raqam bo'yicha qidiruv, `?ordering=` — saralash.
    Standart tartib qiyinlik bo'yicha: profildagi chiplar shunday.
    Jadval uchun har masalada eng yaxshi vaqt/xotira va AC olgan tillar
    ham beriladi.
    """

    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    ORDERINGS: dict[str, str] = {
        "-first_ac_at": "-first_ac_at",
        "first_ac_at": "first_ac_at",
        "-difficulty": "-problem__difficulty",
        "difficulty": "problem__difficulty",
        "title": "problem__title",
    }

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        from ratings.serializers import SolvedProblemSerializer

        return SolvedProblemSerializer

    def get_queryset(self) -> QuerySet[Any]:
        from ratings.models import UserSolvedProblem

        user = get_object_or_404(User, username=self.kwargs["username"], is_active=True)
        qs = UserSolvedProblem.objects.filter(user=user).select_related("problem")
        q = self.request.query_params.get("q", "").strip()
        if q:
            match = Q(problem__title__icontains=q)
            if q.lstrip("#").isdigit():
                match |= Q(problem__code=int(q.lstrip("#")))
            qs = qs.filter(match)
        ordering = self.ORDERINGS.get(
            self.request.query_params.get("ordering", ""), "-problem__difficulty"
        )
        return qs.order_by(ordering, "pk")

    @extend_schema(
        parameters=[
            OpenApiParameter("q", str),
            OpenApiParameter("ordering", str, enum=list(ORDERINGS)),
        ]
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        rows = list(page if page is not None else queryset)
        context = {**self.get_serializer_context(), "best": _best_accepted(rows)}
        data = self.get_serializer(rows, many=True, context=context).data
        return self.get_paginated_response(data) if page is not None else Response(data)


@crud_summaries(
    one="API token",
    many="API tokenlar",
    only=("list", "retrieve", "create", "destroy"),
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
                        "message": f"At most {ApiToken.MAX_ACTIVE_PER_USER} active tokens",
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
                        "message": "Expiry must be in the future",
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
                        "message": "Maximum lifetime is 1 year",
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


@extend_schema(summary="Parolni tiklash havolasini so'rash")
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


@extend_schema(summary="Parolni tiklashni tasdiqlash")
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
                        "message": "This link is invalid or has expired",
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
                        "message": "This link is invalid or has expired",
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


@extend_schema(summary="Mavjud OAuth provayderlar")
class AuthProvidersView(APIView):
    """Sozlangan ijtimoiy kirish provayderlari.

    Frontend shu ro'yxat bo'yicha tugma chizadi: kaliti yo'q provayder
    tugmasi umuman ko'rinmaydi va foydalanuvchi ishlamaydigan yo'lni
    bosmaydi (ADR-0016).
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []
    CACHE_KEY = "auth-providers"
    CACHE_S = 60

    @extend_schema(responses={200: None})
    def get(self, request: Request) -> Response:
        payload = cache_get(self.CACHE_KEY)
        if payload is None:
            payload = {
                "providers": oauth.configured(),
                # Telegram widgetiga bot nomi kerak — u sir emas.
                "telegram_bot": settings.TELEGRAM_BOT_USERNAME,
                # Turnstile SAYT kaliti (9-qaror). Yashirin kalit hech
                # qachon bu yerga tushmaydi; sayt kaliti esa ochiq
                # bo'lishi shart — u brauzerga kerak. Bo'sh satr:
                # «sozlanmagan», ya'ni frontend vidjetni umuman
                # yuklamaydi va tekshiruv o'chiq qoladi.
                "turnstile_site_key": settings.TURNSTILE_SITE_KEY,
            }
            cache_set(self.CACHE_KEY, payload, self.CACHE_S)
        return Response(payload)


#: Bog'lash tokeni sessiyada shuncha turadi. Foydalanuvchi parolini
#: kiritishga ulguradigan, lekin ochiq qolib ketmaydigan muddat.
SOCIAL_LINK_TTL = 600


def record_social_consent(user: User) -> None:
    """Ijtimoiy kirishda shartlar roziligini qayd etadi.

    Email bilan ro'yxatdan o'tganlarda buni `RegisterSerializer` yozadi.
    OAuth'da esa hech qanday forma yo'q — natijada Google/GitHub bilan
    ochilgan hisoblarda `terms_accepted_at` NULL qolib ketardi, ya'ni
    rozilik YOZILMAGAN hisoblar paydo bo'lardi (huquqiy nomuvofiqlik).

    Asos: ijtimoiy tugmalar ostidagi matn «davom etish bilan shartlarga
    rozilik bildirasiz» deydi (`auth.socialConsent`), ya'ni tugmani
    bosish — rozilik. Bu — ommaviy amaliyot.

    Faqat BO'SH bo'lsa yoziladi: bu yerda BIRINCHI rozilik sanasi
    turadi, keyingi kirishlar uni yangilab yuborsa, sana hech narsani
    bildirmay qolardi.
    """
    if user.terms_accepted_at is None:
        user.terms_accepted_at = timezone.now()
        user.save(update_fields=["terms_accepted_at"])


def safe_next(value: str | None) -> str:
    """`?next=` ni xavfsiz ICHKI yo'lga aylantiradi.

    Qiymat ishonchsiz — uni har kim manzil qatorida tahrirlay oladi.
    Tekshirilmasa sayt «ochiq redirect» beradigan bo'lardi: firibgar
    `/api/v1/auth/google/start/?next=https://soxta.uz` ko'rinishidagi
    havolani yuborib, odamni bizning domendan chiqarib yuborishi
    mumkin edi.

    Rad etiladigan shakllar: `https://...` (mutlaq manzil),
    `//evil.com` (protokol-nisbiy — brauzer buni boshqa sayt deb
    o'qiydi) va `/\\evil.com`. Rad etilganda bo'sh satr qaytadi.

    Frontend'dagi `safeNext` (`lib/site.ts`) bilan bir xil qoida. Bu
    yerda ham tekshiriladi: URL'ni frontend chetlab o'tib, to'g'ridan
    to'g'ri API'ga yozish mumkin.
    """
    if not value or not value.startswith("/"):
        return ""
    if value.startswith("//") or value.startswith("/\\"):
        return ""
    return value


@extend_schema(summary="OAuth boshlash")
class SocialStartView(APIView):
    """Provayderning ruxsat sahifasiga yo'naltiradi."""

    permission_classes = [AllowAny]

    @extend_schema(responses={302: None})
    def get(self, request: Request, provider: str) -> HttpResponseRedirect:
        if provider not in oauth.configured() or provider not in oauth.AUTHORIZE:
            return redirect(f"{settings.SITE_URL}/login?social=unavailable")
        state = oauth.new_state()
        # CSRF: qaytgan `state` sessiyadagisi bilan solishtiriladi, ya'ni
        # begona sayt bizning callback'imizga o'z kodini yubora olmaydi.
        request.session["social_state"] = state
        request.session["social_provider"] = provider
        # Qaytish manzili (qaror 1). Har safar YOZILADI — bo'sh qiymat
        # ham: oldingi urinishdan qolgan manzil yangi kirishga
        # «yopishib» qolmasligi kerak.
        request.session["social_next"] = safe_next(request.GET.get("next"))
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
        # PKCE faqat Telegram'da. Uning OIDC oqimi S256 ni qo'llaydi va
        # kodni ushlab qolgan odam uni almashib bera olmasligi kerak.
        # Verifier sessiyada qoladi — callback uni token so'roviga qo'shadi.
        # Google/GitHub uchun tozalanadi: oldingi urinishdan qolgan qiymat
        # yangi kirishga «yopishib» qolmasligi kerak.
        if provider == "telegram":
            verifier, challenge = oauth.pkce_pair()
            request.session["social_pkce"] = verifier
        else:
            challenge = ""
            request.session.pop("social_pkce", None)
        return redirect(oauth.authorize_url(provider, state, challenge))


@extend_schema(summary="OAuth callback")
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

        # PKCE verifier'i `SocialStartView` yozgan. Provayder uni talab
        # qilmasa bo'sh qoladi va o'sha holicha uzatiladi.
        verifier = request.session.pop("social_pkce", "") or ""
        try:
            ident = oauth.identity(provider, request.GET.get("code", ""), verifier)
        except oauth.OAuthError:
            log.exception("social almashuv yiqildi: %s", provider)
            return redirect(f"{home}/login?social=error")

        return self._finish(request, ident)

    def _finish(self, request: Request, ident: oauth.Identity) -> HttpResponseRedirect:
        home = settings.SITE_URL
        # Muvaffaqiyatli kirishdan keyin qayerga. Himoyalangan sahifadan
        # kelgan odam o'sha yerga qaytadi (qaror 1); `link` va xato
        # yo'llari bunga tayanmaydi — ularning o'z manzili bor.
        #
        # Manba — sessiya: uni `SocialStartView` yozadi. Ilgari Telegram
        # bu yerga to'g'ridan-to'g'ri vidjetdan kelardi va manzil so'rovda
        # bo'lardi; oqim OIDC ga o'tgach u ham qolganlar bilan bir xil.
        back = request.session.pop("social_next", "") or safe_next(request.GET.get("next"))
        success = f"{home}{back}" if back else f"{home}/"
        if not ident.uid:
            return redirect(f"{home}/login?social=error")

        link = (
            SocialAccount.objects.filter(provider=ident.provider, uid=ident.uid)
            .select_related("user")
            .first()
        )
        if link is not None and not link.user.is_active:
            if not account.is_anonymized(link.user):
                # Bloklangan hisob — provayder orqali ham kirib bo'lmaydi.
                return redirect(f"{home}/login?social=error")
            # O'chirilgan (anonimlashtirilgan) hisobning qolib ketgan
            # bog'lanishi: egasi shu provayder bilan yangi hisob ochishi
            # kerak, `uniq_social_uid` esa band turardi.
            link.delete()
            link = None

        intent = request.session.pop("social_link_for", None)
        if isinstance(intent, dict) and intent.get("provider") == ident.provider:
            owner_pk = intent.get("user")
            owner = (
                User.objects.filter(pk=owner_pk, is_active=True).first()
                if isinstance(owner_pk, int)
                else None
            )
            if owner is None:
                return redirect(f"{home}/settings/ijtimoiy?social=error")
            if link is not None and link.user_id != owner.pk:
                # Bitta provayder hisobi ikki joyda tura olmaydi —
                # modeldagi `uniq_social_uid` shuni talab qiladi.
                return redirect(f"{home}/settings/ijtimoiy?social=taken")
            SocialAccount.objects.update_or_create(
                user=owner,
                provider=ident.provider,
                defaults={
                    "uid": ident.uid,
                    "email": ident.email,
                    "picture": ident.picture,
                    "username": ident.handle,
                },
            )
            if owner.email_verified_at is None and ident.email.lower() == owner.email.lower():
                owner.email_verified_at = timezone.now()
                owner.save(update_fields=["email_verified_at"])
            record_social_consent(owner)
            return redirect(f"{home}/settings/ijtimoiy?social=linked")

        if link is not None:
            # Rasm va taxallus yangilanadi — ulangan hisobdan olinganda eskisi chiqmasin.
            fresh = {"picture": ident.picture, "username": ident.handle}
            changed = [
                field for field, value in fresh.items() if value and getattr(link, field) != value
            ]
            for field in changed:
                setattr(link, field, fresh[field])
            if changed:
                link.save(update_fields=changed)
            record_social_consent(link.user)
            django_login(request, link.user, backend=DEFAULT_AUTH_BACKEND)
            return redirect(success)

        existing = User.objects.filter(email__iexact=ident.email).first() if ident.email else None
        if existing is not None:
            # ADR-0016: avtomatik bog'lash hisobni egallash yo'li bo'lardi,
            # chunki emailni tasdiqlash majburiy emas.
            request.session["social_pending"] = {
                "provider": ident.provider,
                "uid": ident.uid,
                "email": ident.email,
                "picture": ident.picture,
                "handle": ident.handle,
                "user": existing.pk,
                "at": timezone.now().isoformat(),
            }
            return redirect(f"{home}/login?link={ident.provider}")

        # `kaa` uch harfli — ikki harfga kesish uni `ka` ga, ya'ni
        # mavjud bo'lmagan tilga aylantirardi.
        code = str(getattr(request, "LANGUAGE_CODE", "uz"))
        locale = code if code in User.Locale.values else "uz"
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
            locale=locale,
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])
        SocialAccount.objects.create(
            user=user,
            provider=ident.provider,
            uid=ident.uid,
            email=ident.email,
            picture=ident.picture,
            username=ident.handle,
        )
        record_social_consent(user)
        django_login(request, user, backend=DEFAULT_AUTH_BACKEND)
        return redirect(success)


@extend_schema(summary="Ijtimoiy hisobni ulash")
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
                        "message": "Link request not found or expired",
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
            defaults={
                "uid": pending["uid"],
                "email": pending["email"],
                "picture": pending.get("picture", ""),
                "username": pending.get("handle", ""),
            },
        )
        # Ikki isbot ham qo'lda: provayder manzilni tasdiqlagan va
        # foydalanuvchi hisob parolini bildi. Bundan ortiq tasdiq
        # so'rashning ma'nosi yo'q.
        if user.email_verified_at is None and pending["email"].lower() == user.email.lower():
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at"])
        record_social_consent(user)
        django_login(request, user, backend=DEFAULT_AUTH_BACKEND)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(summary="Sayt ko'rinishi (tema)")
class SiteAppearanceView(APIView):
    """Saytning standart ko'rinishi — ommaviy o'qish (D37).

    Mehmon ham, yangi hisob ham shuni boshlang'ich qiymat sifatida oladi.
    Keshlanadi: u kamdan-kam o'zgaradi, lekin har bir yangi qurilma
    so'raydi.

    Foydalanuvchi O'ZI tanlagach, bu qiymat ustun bo'lmaydi — u faqat
    boshlanish nuqtasi.
    """

    permission_classes = [AllowAny]
    authentication_classes: list[Any] = []
    CACHE_S = 300

    @extend_schema(responses={200: OpenApiResponse(description="Default appearance")})
    def get(self, request: Request) -> Response:
        payload = cache_get("site-appearance")
        if payload is None:
            payload = {"appearance": SiteAppearance.load().appearance or {}}
            cache_set("site-appearance", payload, self.CACHE_S)
        return Response(payload)
