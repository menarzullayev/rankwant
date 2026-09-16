"""Staff (admin UI) — foydalanuvchilar boshqaruvi.

Yaratish va o'chirish YO'Q: foydalanuvchi ro'yxatdan o'tadi, admin uni
bloklaydi (`is_active`) — o'chirmaydi (ledger va reyting tarixi saqlanadi).
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Count, F, Q, QuerySet
from django.db.models.functions import TruncDate
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import AnalyticsEvent, School, User
from core.openapi_docs import crud_summaries
from core.staff import SessionOnly, StaffViewSet
from core.staff_serializers import (
    QvantAdjustSerializer,
    StaffNotifySerializer,
    StaffSchoolSerializer,
    StaffUserSerializer,
)
from notifications import services as notifications
from notifications.models import Notification
from qvant import ledger
from qvant.models import QvantTransaction


@crud_summaries(
    one="foydalanuvchi",
    many="foydalanuvchilar",
    only=("list", "retrieve", "create", "partial_update"),
    extra={
        "notify": "Bitta foydalanuvchiga bildirishnoma",
        "broadcast": "Hammaga bildirishnoma yuborish",
    },
)
class StaffUserViewSet(StaffViewSet):
    serializer_class = StaffUserSerializer
    lookup_field = "username"
    #: Standart router shabloni nuqtani kesadi — `a.b` username 404 berardi.
    lookup_value_regex = "[^/]+"
    search_fields = ["username", "display_name", "email"]
    ordering_fields = ["date_joined", "rating_skills"]
    ordering = ["-date_joined", "-pk"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.annotate(qvant_balance=F("wallet__balance"))

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        raise MethodNotAllowed("POST")

    @action(detail=True, methods=["post"])
    def qvant(self, request: Request, username: str | None = None) -> Response:
        """Qvant tuzatish: musbat — kunlik shiftsiz kredit, manfiy — debit."""
        user = self.get_object()
        ser = QvantAdjustSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        amount: int = ser.validated_data["amount"]
        note: str = ser.validated_data["note"]
        ref = {"ref_type": "admin", "ref_id": note[:64]}
        try:
            if amount > 0:
                tx = ledger.credit(
                    user, amount, QvantTransaction.Reason.ADMIN, respect_cap=False, **ref
                )
            else:
                tx = ledger.debit(user, -amount, QvantTransaction.Reason.ADMIN, **ref)
        except ledger.InsufficientBalance as exc:
            raise ValidationError({"amount": f"Balans yetarli emas: {exc}"}) from exc
        assert tx is not None  # respect_cap=False — kredit har doim yoziladi
        return Response({"amount": tx.amount, "balance": tx.balance_after})

    @action(detail=True, methods=["post"])
    def notify(self, request: Request, username: str | None = None) -> Response:
        user = self.get_object()
        ser = StaffNotifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        n = notifications.notify(
            user,
            Notification.Kind.SYSTEM,
            ser.validated_data["title"],
            body=ser.validated_data["body"],
            ref_type="admin",
        )
        return Response({"id": n.pk if n else None}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def broadcast(self, request: Request) -> Response:
        ser = StaffNotifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        count = notifications.notify_many(
            User.objects.filter(is_active=True).iterator(),
            Notification.Kind.SYSTEM,
            ser.validated_data["title"],
            body=ser.validated_data["body"],
            ref_type="admin",
        )
        return Response({"count": count}, status=status.HTTP_201_CREATED)


class StaffSchoolViewSet(StaffViewSet):
    """Maktab katalogi — to'liq CRUD (ADR-0017).

    Nega bu API kerak bo'ldi: ADR "moderator admin paneldan to'ldiradi"
    deydi, lekin amalda uni to'ldirishning YO'LI yo'q edi —
    `ADMIN_ENABLED` production'da ataylab o'chiq, `SchoolViewSet` esa
    faqat o'qish uchun. Ya'ni maktab reytingi va sinfdoshlar bo'sh
    qolib ketardi.

    Qolgan staff yuzalari bilan bir xil qoida: faqat `is_staff` va faqat
    sessiya (PAT emas — `StaffViewSet` dagi `SessionOnly`).
    """

    serializer_class = StaffSchoolSerializer
    search_fields = ["name", "region", "district", "city"]
    ordering_fields = ["name", "region", "created_at"]
    ordering = ["name", "pk"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self) -> QuerySet[School]:
        # `members` — katalog yozuvini o'chirishdan oldin moderator
        # "nechta odam shu maktabda" ekanini ko'rishi kerak: o'chirilsa
        # ular `school_ref` ni yo'qotadi (FK `SET_NULL`).
        return School.objects.annotate(
            members=Count("students", filter=Q(students__is_active=True))
        )


class StaffAnalyticsView(APIView):
    """Ro'yxatdan o'tish voronkasi — `AnalyticsEvent` dan jamlanadi.

    Nega kerak: hodisalar yozila boshlagan edi, lekin ularni KO'RISH
    yo'li yo'q edi — ya'ni yig'ilgan ma'lumot ishlatilmayotgan edi
    (qaror 7). Qaysi qadamda odam ketayotganini bilmasdan formani
    optimallashtirib bo'lmaydi.

    SESSIYA bo'yicha sanaladi, xom hodisa bo'yicha emas: bitta odam
    xatoni o'n marta ko'rishi mumkin, «qancha odam shu qadamda
    to'xtadi» degan savolga esa faqat sessiya javob beradi.

    Faqat o'qish. `StaffViewSet` dan meros olmaydi — bu agregatsiya,
    CRUD emas, ya'ni ro'yxat/paginatsiya tushunchalari yo'q.
    """

    permission_classes = [IsAdminUser, SessionOnly]

    #: Voronka ketma-ketligi — ulushlar BIRINCHI qadamga nisbatan.
    #: `auth.step2_*` bu yerda YO'Q: ular ketma-ket qadam emas, tarmoq
    #: (saqlash yoki o'tkazib yuborish) — alohida ko'rsatiladi.
    FUNNEL = ("auth.form_started", "auth.register_done")

    #: 2-qadamning ikki chiqishi.
    STEP2 = ("auth.step2_saved", "auth.step2_skipped")

    DEFAULT_DAYS = 30
    MAX_DAYS = 365

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "days",
                int,
                description="Oyna uzunligi (kun). 1–365, standart 30.",
            )
        ],
        responses={200: OpenApiResponse(description="Voronka jamlanmasi")},
    )
    def get(self, request: Request) -> Response:
        days = self._window(request)
        since = timezone.now() - timedelta(days=days)
        events = AnalyticsEvent.objects.filter(created_at__gte=since)
        return Response(
            {
                "window_days": days,
                "total_events": events.count(),
                "funnel": self._funnel(events),
                "step2": self._step2(events),
                "variant": self._by_variant(events),
                "errors": self._errors(events),
                "locales": self._by_locale(events),
                "countries": self._by_country(events),
                "daily": self._daily(events),
            }
        )

    def _window(self, request: Request) -> int:
        raw = request.query_params.get("days", str(self.DEFAULT_DAYS))
        try:
            days = int(raw)
        except (TypeError, ValueError):
            raise ValidationError({"days": "Butun son bo'lishi kerak"}) from None
        return min(max(days, 1), self.MAX_DAYS)

    def _counts(self, events: QuerySet[AnalyticsEvent], names: tuple[str, ...]) -> dict[str, int]:
        rows = (
            events.filter(name__in=names)
            .values("name")
            .annotate(sessions=Count("session_key", distinct=True))
        )
        return {row["name"]: row["sessions"] for row in rows}

    def _funnel(self, events: QuerySet[AnalyticsEvent]) -> list[dict[str, Any]]:
        counts = self._counts(events, self.FUNNEL)
        first = counts.get(self.FUNNEL[0], 0)
        return [
            {
                "name": name,
                "sessions": counts.get(name, 0),
                # Ulush BIRINCHI qadamga nisbatan: «necha foiz yetib
                # keldi» degan savolga shu javob beradi. Har bir oldingi
                # qadamga nisbatan hisoblansa, qaysi qadam eng katta
                # yo'qotish ekani ko'rinmay qolardi.
                "share": round(counts.get(name, 0) * 100 / first, 1) if first else 0.0,
            }
            for name in self.FUNNEL
        ]

    def _step2(self, events: QuerySet[AnalyticsEvent]) -> dict[str, Any]:
        counts = self._counts(events, self.STEP2)
        saved = counts.get("auth.step2_saved", 0)
        skipped = counts.get("auth.step2_skipped", 0)
        total = saved + skipped
        return {
            "saved": saved,
            "skipped": skipped,
            # Eng muhim ko'rsatkich (qaror 17): 2-qadamni qancha odam
            # to'ldirmasligini ko'rsatadi.
            "skipped_share": round(skipped * 100 / total, 1) if total else 0.0,
        }

    def _by_variant(self, events: QuerySet[AnalyticsEvent]) -> dict[str, Any]:
        """A/B natijasi — ro'yxatdan o'tishni TUGATGAN sessiyalar guruh bo'yicha.

        Guruh har bir hodisaning `props.exp` maydonida keladi
        (`lib/analytics.ts` uni avtomatik qo'shadi). Taqqoslanadigan
        ko'rsatkich — aynan `auth.register_done`: ikkala guruhda ham
        farq qiladigan YAGONA narsa viloyat qachon so'ralishi bo'lgani
        uchun, «erta so'rash odamni qaytarib yubordimi» degan savolga
        javob shu yerda.

        Guruh yo'q (cookie o'chirilgan yoki juda eski sessiya) bo'lsa
        hodisa hisobga OLINMAYDI — uni «nazorat» deb yozish natijani
        buzardi.
        """
        rows = (
            events.filter(name="auth.register_done")
            .values("props__exp")
            .annotate(sessions=Count("session_key", distinct=True))
        )
        counts = {"a": 0, "b": 0}
        for row in rows:
            key = row["props__exp"]
            if key in counts:
                counts[key] = row["sessions"]
        total = counts["a"] + counts["b"]
        return {
            "control": counts["a"],
            "variant": counts["b"],
            "total": total,
            # Guruhlar teng bo'lmasa (cookie tozalangan, eski sessiya)
            # bu ko'rinadi — natijani o'qishdan oldin tekshirilsin.
            "control_share": round(counts["a"] * 100 / total, 1) if total else 0.0,
        }

    def _errors(self, events: QuerySet[AnalyticsEvent]) -> list[dict[str, Any]]:
        """Xato sabablari — qaysi maydon eng ko'p to'xtatayotgani.

        `props__reason` — JSON maydoni ICHIDAGI kalit; Django uni SQL'da
        ajratib oladi, ya'ni Python'da qayta ishlash shart emas.
        """
        rows = (
            events.filter(name="auth.form_error")
            .values("props__reason")
            .annotate(sessions=Count("session_key", distinct=True))
            .order_by("-sessions")[:12]
        )
        return [
            {"reason": row["props__reason"] or "—", "sessions": row["sessions"]} for row in rows
        ]

    def _by_locale(self, events: QuerySet[AnalyticsEvent]) -> list[dict[str, Any]]:
        rows = (
            events.exclude(locale="")
            .values("locale")
            .annotate(sessions=Count("session_key", distinct=True))
            .order_by("-sessions")[:12]
        )
        return [{"locale": row["locale"], "sessions": row["sessions"]} for row in rows]

    def _by_country(self, events: QuerySet[AnalyticsEvent]) -> list[dict[str, Any]]:
        """Mamlakat foydalanuvchidan olinadi — hodisaning o'zida yo'q.

        Kirilmagan sessiyalarda `user` NULL, ya'ni ular bu ro'yxatga
        tushmaydi. Bu TO'G'RI: qaysi mamlakatdan ro'yxatdan o'tish
        tugallanayotgani muhim, qayerdan boshlangani emas.

        DIQQAT: `.exclude(user__country="")` yolg'iz NULL'ni chiqarib
        TASHLAMAYDI. Django uni `NOT (x = '' AND x IS NOT NULL)` ga
        aylantiradi, NULL uchun esa bu ifoda TRUE bo'lib qoladi — ya'ni
        anonim hodisalar «mamlakat: null» bo'lib ro'yxatga tushardi.
        Shuning uchun `user` alohida istisno qilinadi.
        """
        rows = (
            events.exclude(user__isnull=True)
            .exclude(user__country="")
            .values("user__country")
            .annotate(sessions=Count("session_key", distinct=True))
            .order_by("-sessions")[:12]
        )
        return [{"country": row["user__country"], "sessions": row["sessions"]} for row in rows]

    def _daily(self, events: QuerySet[AnalyticsEvent]) -> list[dict[str, Any]]:
        """Kunlik ketma-ketlik — grafik uchun.

        Bo'sh kunlar QO'SHILMAYDI: grafik ularni o'zi to'ldiradi, bu
        yerda esa har bir sana uchun qator yasash so'rovni og'irlashtirardi.
        """
        rows = (
            events.filter(name__in=self.FUNNEL)
            .annotate(day=TruncDate("created_at"))
            .values("day", "name")
            .annotate(sessions=Count("session_key", distinct=True))
            .order_by("day")
        )
        by_day: dict[str, dict[str, int]] = {}
        for row in rows:
            by_day.setdefault(row["day"].isoformat(), {})[row["name"]] = row["sessions"]
        return [
            {
                "date": day,
                "started": counts.get("auth.form_started", 0),
                "done": counts.get("auth.register_done", 0),
            }
            for day, counts in sorted(by_day.items())
        ]
