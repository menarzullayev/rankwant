from django.urls import include, path
from rest_framework.routers import DefaultRouter

from courses import author_views, views

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="course")
# The studio lives under its own prefix: `courses/mine/` would be read as the
# public page of a course whose slug is "mine".
router.register("studio/courses", author_views.MineCourseViewSet, basename="studio-course")
router.register(
    r"studio/courses/(?P<course_slug>[-\w]+)/modules",
    author_views.MineModuleViewSet,
    basename="studio-course-module",
)
router.register(
    r"studio/courses/(?P<course_slug>[-\w]+)/sections",
    author_views.MineSectionViewSet,
    basename="studio-course-section",
)
router.register(
    r"studio/courses/(?P<course_slug>[-\w]+)/lessons",
    author_views.MineLessonViewSet,
    basename="studio-course-lesson",
)
router.register("staff/courses", author_views.StaffCourseViewSet, basename="staff-course")

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
