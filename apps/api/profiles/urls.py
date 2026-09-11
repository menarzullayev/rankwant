from django.urls import path

from profiles import views

urlpatterns = [
    path("skills/catalog/", views.SkillCatalogView.as_view(), name="skill-catalog"),
    path(
        "technologies/catalog/",
        views.TechnologyCatalogView.as_view(),
        name="technology-catalog",
    ),
    path("me/skills/", views.MySkillsView.as_view(), name="me-skills"),
    path("me/technologies/", views.MyTechnologiesView.as_view(), name="me-technologies"),
    path("me/educations/", views.MyEducationsView.as_view(), name="me-educations"),
    path("me/work/", views.MyWorkView.as_view(), name="me-work"),
    path("me/external/", views.MyExternalView.as_view(), name="me-external"),
    path("me/teams/", views.MyTeamsView.as_view(), name="me-teams"),
    path("teams/join/", views.TeamJoinView.as_view(), name="team-join"),
    path("teams/<int:pk>/", views.TeamDetailView.as_view(), name="team-detail"),
    path("teams/<int:pk>/refresh-code/", views.TeamRefreshView.as_view(), name="team-refresh"),
    path("teams/<int:pk>/leave/", views.TeamLeaveView.as_view(), name="team-leave"),
    path(
        "teams/<int:pk>/members/<str:username>/",
        views.TeamMemberView.as_view(),
        name="team-member",
    ),
    path("users/<str:username>/profile/", views.PublicProfileView.as_view(), name="user-profile"),
    path("users/<str:username>/activity/", views.ActivityView.as_view(), name="user-activity"),
    path(
        "users/<str:username>/achievements/",
        views.AchievementsView.as_view(),
        name="user-achievements",
    ),
    path("users/<str:username>/purchases/", views.PurchasesView.as_view(), name="user-purchases"),
    path("users/<str:username>/follow/", views.FollowView.as_view(), name="user-follow"),
    path("users/<str:username>/stats/", views.UserStatsView.as_view(), name="user-stats"),
    path("users/<str:username>/calendar/", views.UserCalendarView.as_view(), name="user-calendar"),
    path(
        "users/<str:username>/problem-map/",
        views.UserProblemMapView.as_view(),
        name="user-problem-map",
    ),
    path(
        "users/<str:username>/rating-series/",
        views.UserRatingSeriesView.as_view(),
        name="user-rating-series",
    ),
    path("users/<str:username>/topics/", views.UserTopicsView.as_view(), name="user-topics"),
    path("users/<str:username>/contests/", views.UserContestsView.as_view(), name="user-contests"),
    path(
        "users/<str:username>/followers/",
        views.FollowListView.as_view(direction="followers"),
        name="user-followers",
    ),
    path(
        "users/<str:username>/following/",
        views.FollowListView.as_view(direction="following"),
        name="user-following",
    ),
]
