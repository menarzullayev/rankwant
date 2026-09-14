"""Roadmap URL'lari.

⚠️ Prefiks **`platform-roadmap`**, `roadmap` EMAS: `content` app ida
`/roadmaps/` (ta'lim traektoriyasi) allaqachon bor va DRF router nomlari
ham band (`roadmap`, `staff-roadmap`). Bir harf farq qiladigan ikki
manzil kodda ham, havolada ham adashtiradi.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from roadmap import views
from roadmap.staff_views import StaffRoadmapCommentViewSet, StaffRoadmapViewSet

router = DefaultRouter()
router.register("platform-roadmap", views.RoadmapItemViewSet, basename="platform-roadmap")
router.register("staff/platform-roadmap", StaffRoadmapViewSet, basename="staff-platform-roadmap")
router.register(
    "staff/platform-roadmap-comments",
    StaffRoadmapCommentViewSet,
    basename="staff-platform-roadmap-comment",
)

urlpatterns = [path("", include(router.urls))]
