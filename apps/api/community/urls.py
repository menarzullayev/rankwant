from django.urls import include, path
from rest_framework.routers import DefaultRouter

from community import views

router = DefaultRouter()
router.register("comments", views.CommentViewSet, basename="comment")
router.register("staff/community/comments", views.StaffCommentViewSet, basename="staff-comment")

urlpatterns = [
    path(
        "discussions/problem/<str:ref>/",
        views.ProblemDiscussionView.as_view(),
        name="problem-discussion",
    ),
    path("", include(router.urls)),
]
