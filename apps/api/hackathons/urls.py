from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hackathons import views
from hackathons.staff_views import StaffHackathonViewSet

router = DefaultRouter()
router.register("hackathons", views.HackathonViewSet, basename="hackathon")
router.register("staff/hackathons", StaffHackathonViewSet, basename="staff-hackathon")

urlpatterns = [path("", include(router.urls))]
