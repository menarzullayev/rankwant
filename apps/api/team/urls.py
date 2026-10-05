from django.urls import include, path
from rest_framework.routers import DefaultRouter

from team import staff_views, views

router = DefaultRouter()
router.register(
    "staff/team/departments", staff_views.StaffDepartmentViewSet, basename="staff-team-department"
)
router.register("staff/team/roles", staff_views.StaffRoleViewSet, basename="staff-team-role")
router.register("staff/team/members", staff_views.StaffMemberViewSet, basename="staff-team-member")

urlpatterns = [
    path("team/", views.TeamView.as_view(), name="team"),
    path("", include(router.urls)),
]
