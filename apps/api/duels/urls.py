from django.urls import include, path
from rest_framework.routers import DefaultRouter

from duels import views
from duels.staff_views import StaffDuelViewSet

router = DefaultRouter()
router.register("duels", views.DuelViewSet, basename="duel")
router.register("staff/duels", StaffDuelViewSet, basename="staff-duel")

urlpatterns = [path("", include(router.urls))]
