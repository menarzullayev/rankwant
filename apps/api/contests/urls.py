from django.urls import include, path
from rest_framework.routers import DefaultRouter

from contests import views

router = DefaultRouter()
router.register("contests", views.ContestViewSet, basename="contest")

urlpatterns = [
    path("contests/<slug:slug>/standings/stream/", views.standings_stream, name="standings-stream"),
    path("", include(router.urls)),
]
