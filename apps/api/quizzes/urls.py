from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quizzes import author_views, views
from quizzes.staff_quiz_views import StaffQuizViewSet
from quizzes.staff_views import StaffQuestionViewSet

router = DefaultRouter()
# `mine` BEFORE `quizzes`: otherwise `quizzes/<slug>/` takes `quizzes/mine/`.
router.register("quizzes/mine", author_views.MyQuizViewSet, basename="mine-quiz")
router.register("questions/mine", author_views.MyQuestionViewSet, basename="mine-question")
router.register("question-folders", author_views.FolderViewSet, basename="question-folder")
router.register("quizzes", views.QuizViewSet, basename="quiz")
router.register("staff/questions", StaffQuestionViewSet, basename="staff-question")
router.register("staff/quizzes", StaffQuizViewSet, basename="staff-quiz")

urlpatterns = [path("", include(router.urls))]
