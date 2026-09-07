from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quizzes import views
from quizzes.staff_views import StaffQuestionViewSet

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz")
router.register("staff/questions", StaffQuestionViewSet, "staff-question")  # staff: questions

urlpatterns = [path("", include(router.urls))]
