from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core import account_views, views
from core.school_views import SchoolViewSet
from core.staff_views import (
    StaffAnalyticsView,
    StaffEmailQuotaView,
    StaffSchoolViewSet,
    StaffUserViewSet,
)

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")
router.register("schools", SchoolViewSet, basename="school")
router.register("me/tokens", views.ApiTokenViewSet, basename="apitoken")
router.register("staff/users", StaffUserViewSet, basename="staff-user")  # staff: users
# Maktab katalogi (ADR-0017) — moderatorsiz u bo'sh qolardi.
router.register("staff/schools", StaffSchoolViewSet, basename="staff-school")

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("slo/", views.SloView.as_view(), name="slo"),
    path("appearance/", views.SiteAppearanceView.as_view(), name="site-appearance"),
    path("stats/", views.PlatformStatsView.as_view(), name="platform-stats"),
    path("calendar/", views.CalendarView.as_view(), name="calendar"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    # Funnel hodisalari (qaror 17) — kirilmagan foydalanuvchi ham yuboradi.
    path(
        "analytics/events/",
        views.AnalyticsEventView.as_view(),
        name="analytics-events",
    ),
    # Voronka dashboardi (qaror 7) — yozilgan hodisalarni KO'RISH yo'li.
    # `analytics/events/` yozadi (ochiq), bu esa faqat o'qiydi (staff).
    # Brauzer xatolari (qaror 2026-09-24) — Sentry o'rniga oddiy
    # jurnal. `analytics/events/` bilan bir xil sabab: kirilmagan
    # foydalanuvchining xatosi ham kerak.
    path(
        "client-logs/",
        views.ClientLogView.as_view(),
        name="client-logs",
    ),
    path(
        "staff/analytics/",
        StaffAnalyticsView.as_view(),
        name="staff-analytics",
    ),
    # Email kvota paneli — «qaysi provayder qancha sarfladi» savoli.
    # Staff panel `/admin/*` da ishlaydi, Django admin esa productionda
    # o'chirilgan (`ADMIN_ENABLED=False`) — shuning uchun alohida yo'l.
    path(
        "staff/email-quota/",
        StaffEmailQuotaView.as_view(),
        name="staff-email-quota",
    ),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/providers/", views.AuthProvidersView.as_view(), name="auth-providers"),
    path("auth/username-check/", views.UsernameCheckView.as_view(), name="username-check"),
    # `auth/social/<provider>/link-start/` yo'li OLIB TASHLANDI: u faqat
    # Telegram vidjeti uchun kerak edi (callback'i `state` siz GET bo'lgani
    # uchun niyat alohida POST bilan belgilanardi). Oqim OIDC ga o'tgach
    # niyatni `SocialStartView` sessiyaga o'zi yozadi — Google/GitHub kabi.
    path(
        "auth/social/<str:provider>/",
        views.SocialUnlinkView.as_view(),
        name="social-unlink",
    ),
    path("auth/email/verify/", views.EmailVerifyView.as_view(), name="email-verify"),
    path("auth/email/resend/", views.EmailVerifyResendView.as_view(), name="email-verify-resend"),
    path("auth/link/", views.SocialLinkView.as_view(), name="social-link"),
    # Telegram uchun ALOHIDA callback yo'li yo'q edi: vidjet imzolangan
    # ma'lumotni to'g'ridan-to'g'ri yuborardi va kod almashinuvi bo'lmasdi.
    # Endi u ham OIDC, ya'ni quyidagi umumiy `<provider>/callback/` uni
    # qabul qiladi. Manzil o'zgarmadi — @BotFather'da ro'yxatga olingan
    # `redirect_uri` aynan shu.
    path("auth/<str:provider>/start/", views.SocialStartView.as_view(), name="social-start"),
    path(
        "auth/<str:provider>/callback/",
        views.SocialCallbackView.as_view(),
        name="social-callback",
    ),
    path(
        "auth/password-reset/",
        views.PasswordResetRequestView.as_view(),
        name="password-reset",
    ),
    path(
        "auth/password-reset/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("me/", views.MeView.as_view(), name="me"),
    path("me/export/", views.MeExportView.as_view(), name="me-export"),
    path("me/password/", account_views.PasswordChangeView.as_view(), name="me-password"),
    path("me/email/", account_views.EmailChangeView.as_view(), name="me-email"),
    path("me/username/", account_views.UsernameChangeView.as_view(), name="me-username"),
    path("me/sessions/", account_views.SessionListView.as_view(), name="me-sessions"),
    path("me/sessions/<int:pk>/", account_views.SessionDetailView.as_view(), name="me-session"),
    path("me/avatar/", account_views.AvatarView.as_view(), name="me-avatar"),
    path("me/avatar/import/", account_views.AvatarImportView.as_view(), name="me-avatar-import"),
    path("avatars/<str:name>", account_views.avatar_file, name="avatar-file"),
    path(
        "users/<str:username>/rating-history/",
        views.RatingHistoryView.as_view(),
        name="rating-history",
    ),
    path(
        "users/<str:username>/solved/", views.SolvedProblemsView.as_view(), name="solved-problems"
    ),
    path("", include(router.urls)),
]
