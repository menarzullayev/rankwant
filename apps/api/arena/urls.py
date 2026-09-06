from django.urls import include, path
from rest_framework.routers import DefaultRouter

from arena import views

router = DefaultRouter()
router.register("arena", views.ArenaViewSet, basename="arena")

urlpatterns = [
    path("arena/<slug:slug>/standings/stream/", views.standings_stream, name="arena-stream"),
    path("", include(router.urls)),
]
