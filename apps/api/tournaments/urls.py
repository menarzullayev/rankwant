from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tournaments import views
from tournaments.staff_views import StaffTournamentViewSet

router = DefaultRouter()
router.register("tournaments", views.TournamentViewSet, basename="tournament")
router.register("staff/tournaments", StaffTournamentViewSet, basename="staff-tournament")

urlpatterns = [path("", include(router.urls))]
