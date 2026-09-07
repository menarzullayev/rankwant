from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quizzes import views
from quizzes.staff_quiz_views import StaffQuestionLookupViewSet, StaffQuizViewSet

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz")
router.register("staff/quizzes", StaffQuizViewSet, basename="staff-quiz")  # staff: quizzes
router.register(
    "staff/questions", StaffQuestionLookupViewSet, basename="staff-question"
)  # staff: questions (fallback)

urlpatterns = [path("", include(router.urls))]
