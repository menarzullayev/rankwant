from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quizzes import views
from quizzes.staff_quiz_views import StaffQuizViewSet
from quizzes.staff_views import StaffQuestionViewSet

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz")
router.register("staff/questions", StaffQuestionViewSet, basename="staff-question")
router.register("staff/quizzes", StaffQuizViewSet, basename="staff-quiz")

urlpatterns = [path("", include(router.urls))]
