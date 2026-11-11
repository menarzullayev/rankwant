from django.urls import include, path
from rest_framework.routers import DefaultRouter

from community import views

router = DefaultRouter()
router.register("comments", views.CommentViewSet, basename="comment")
router.register("blogs", views.EntryViewSet, basename="entry")
router.register("staff/community/entries", views.StaffEntryViewSet, basename="staff-entry")
router.register("staff/community/comments", views.StaffCommentViewSet, basename="staff-comment")

urlpatterns = [
    path(
        "discussions/problem/<str:ref>/",
        views.DiscussionView.as_view(kind="problem"),
        name="problem-discussion",
    ),
    path(
        "discussions/entry/<str:ref>/",
        views.DiscussionView.as_view(kind="entry"),
        name="entry-discussion",
    ),
    path("community/karma/", views.KarmaTopView.as_view(), name="karma-top"),
    path("me/content-reports/", views.MyContentReportsView.as_view(), name="my-content-reports"),
    path("", include(router.urls)),
]
