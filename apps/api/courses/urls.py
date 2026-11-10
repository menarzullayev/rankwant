from django.urls import include, path
from rest_framework.routers import DefaultRouter

from courses import views

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="course")

urlpatterns = [
    path("me/courses/", views.MyCoursesView.as_view(), name="my-courses"),
    path(
        "courses/<slug:slug>/lessons/<int:lesson_id>/",
        views.LessonDetailView.as_view(),
        name="course-lesson",
    ),
    path(
        "courses/<slug:slug>/lessons/<int:lesson_id>/complete/",
        views.LessonCompleteView.as_view(),
        name="course-lesson-complete",
    ),
    path("", include(router.urls)),
]
