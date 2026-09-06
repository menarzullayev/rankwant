from django.urls import include, path
from rest_framework.routers import DefaultRouter

from duels import views

router = DefaultRouter()
router.register("duels", views.DuelViewSet, basename="duel")

urlpatterns = [path("", include(router.urls))]
