"""API v1 marshrutlari — 05-domain-model § API resurs nomlari."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("", include("core.urls")),
    path("", include("problems.urls")),
    path("", include("judging.urls")),
    path("", include("contests.urls")),
    path("", include("qvant.urls")),
    path("", include("notifications.urls")),
    path("", include("blog.urls")),
    path("", include("content.urls")),
    path("", include("classroom.urls")),
    path("", include("quizzes.urls")),
    path("", include("arena.urls")),
    path("", include("duels.urls")),
]
