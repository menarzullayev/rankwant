from django.urls import include, path
from rest_framework.routers import DefaultRouter

from contests import views
from contests.staff_views import StaffContestViewSet

router = DefaultRouter()
router.register("contests", views.ContestViewSet, basename="contest")
router.register("staff/contests", StaffContestViewSet, basename="staff-contest")

urlpatterns = [
    path("", include(router.urls)),
]
