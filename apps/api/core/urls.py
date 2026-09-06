from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core import views

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")
router.register("me/tokens", views.ApiTokenViewSet, basename="apitoken")

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
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
