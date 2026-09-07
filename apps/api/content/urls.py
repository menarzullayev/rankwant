from django.urls import include, path
from rest_framework.routers import DefaultRouter

from content import staff_views, views

router = DefaultRouter()
router.register("articles", views.ArticleViewSet, basename="article")
router.register("roadmaps", views.RoadmapViewSet, basename="roadmap")
router.register("staff/articles", staff_views.StaffArticleViewSet, basename="staff-article")
router.register("staff/roadmaps", staff_views.StaffRoadmapViewSet, basename="staff-roadmap")

urlpatterns = [path("", include(router.urls))]
