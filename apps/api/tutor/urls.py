from django.urls import path
from rest_framework.routers import SimpleRouter

from tutor.views import (
    ProblemTutorReportView,
    ProblemTutorView,
    StaffTutorBudgetView,
    StaffTutorReportViewSet,
)

router = SimpleRouter()
router.register("staff/tutor-reports", StaffTutorReportViewSet, basename="staff-tutor-report")

urlpatterns = [
    path("problems/<slug:slug>/tutor/", ProblemTutorView.as_view(), name="problem-tutor"),
    path(
        "problems/<slug:slug>/tutor/reports/",
        ProblemTutorReportView.as_view(),
        name="problem-tutor-report",
    ),
    path("staff/tutor/budget/", StaffTutorBudgetView.as_view(), name="staff-tutor-budget"),
    *router.urls,
]
