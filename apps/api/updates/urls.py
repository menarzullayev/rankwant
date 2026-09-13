from django.urls import include, path
from rest_framework.routers import DefaultRouter

from updates import views
from updates.staff_views import StaffUpdateViewSet

router = DefaultRouter()
router.register("updates", views.SystemUpdateViewSet, basename="update")
router.register("staff/updates", StaffUpdateViewSet, basename="staff-update")

urlpatterns = [path("", include(router.urls))]
