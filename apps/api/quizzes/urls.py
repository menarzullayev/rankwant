from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quizzes import views

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz")

urlpatterns = [path("", include(router.urls))]
