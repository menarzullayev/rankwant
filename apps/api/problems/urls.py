from django.urls import include, path
from rest_framework.routers import DefaultRouter

from problems import staff_views, views

router = DefaultRouter()
router.register("problems", views.ProblemViewSet, basename="problem")
router.register("topics", views.TopicViewSet, basename="topic")
router.register("languages", views.LanguageViewSet, basename="language")
router.register("staff/problems", staff_views.StaffProblemViewSet, basename="staff-problem")
router.register("staff/topics", staff_views.StaffTopicViewSet, basename="staff-topic")

urlpatterns = [
    path("problems/recommendation/", views.RecommendationView.as_view(), name="recommendation"),
    path("problems/progress/", views.ProgressView.as_view(), name="problem-progress"),
    path("", include(router.urls)),
]
