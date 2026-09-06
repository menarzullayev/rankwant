from django.urls import include, path
from rest_framework.routers import DefaultRouter

from problems import views

router = DefaultRouter()
router.register("problems", views.ProblemViewSet, basename="problem")
router.register("topics", views.TopicViewSet, basename="topic")
router.register("languages", views.LanguageViewSet, basename="language")

urlpatterns = [path("", include(router.urls))]
