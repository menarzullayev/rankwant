from django.urls import include, path
from rest_framework.routers import DefaultRouter

from problems import author_views, media_views, staff_views, views

router = DefaultRouter()
router.register("problems/mine", author_views.MineProblemViewSet, basename="mine-problem")
router.register("problems", views.ProblemViewSet, basename="problem")
router.register("topics", views.TopicViewSet, basename="topic")
router.register("languages", views.LanguageViewSet, basename="language")
router.register("staff/problems", staff_views.StaffProblemViewSet, basename="staff-problem")
router.register("staff/topics", staff_views.StaffTopicViewSet, basename="staff-topic")
router.register(
    "staff/problem-reports",
    staff_views.StaffProblemReportViewSet,
    basename="staff-problem-report",
)

urlpatterns = [
    path("problems/recommendation/", views.RecommendationView.as_view(), name="recommendation"),
    path("problems/progress/", views.ProgressView.as_view(), name="problem-progress"),
    path("problems/skills/", views.TopicSkillsView.as_view(), name="problem-skills"),
    path(
        "problems/<slug:slug>/solvers/",
        views.ProblemSolversView.as_view(),
        name="problem-solvers",
    ),
    path(
        "problems/<slug:slug>/stats/",
        views.ProblemStatsView.as_view(),
        name="problem-stats",
    ),
    path("media/<path:path>", media_views.media, name="media"),
    path("", include(router.urls)),
]
