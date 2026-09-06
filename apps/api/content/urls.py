from django.urls import include, path
from rest_framework.routers import DefaultRouter

from content import views

router = DefaultRouter()
router.register("articles", views.ArticleViewSet, basename="article")
router.register("roadmaps", views.RoadmapViewSet, basename="roadmap")

urlpatterns = [path("", include(router.urls))]
