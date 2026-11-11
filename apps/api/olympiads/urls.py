from django.urls import path

from olympiads import views

urlpatterns = [
    path("olympiads/", views.SeasonListView.as_view(), name="olympiad-seasons"),
    path("olympiads/events/<slug:slug>/", views.EventDetailView.as_view(), name="olympiad-event"),
    path(
        "olympiads/events/<slug:slug>/tasks/<slug:task>/",
        views.TaskDetailView.as_view(),
        name="olympiad-task",
    ),
    path(
        "olympiads/participants/<slug:slug>/",
        views.ParticipantView.as_view(),
        name="olympiad-participant",
    ),
]
