from django.urls import path

from tutor.views import ProblemTutorView

urlpatterns = [
    path("problems/<slug:slug>/tutor/", ProblemTutorView.as_view(), name="problem-tutor"),
]
