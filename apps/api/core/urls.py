from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core import views
from core.staff_views import StaffUserViewSet

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")
router.register("me/tokens", views.ApiTokenViewSet, basename="apitoken")
router.register("staff/users", StaffUserViewSet, basename="staff-user")  # staff: users

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("stats/", views.PlatformStatsView.as_view(), name="platform-stats"),
    path("calendar/", views.CalendarView.as_view(), name="calendar"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/providers/", views.AuthProvidersView.as_view(), name="auth-providers"),
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
