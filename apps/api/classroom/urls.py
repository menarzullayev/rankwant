from django.urls import include, path
from rest_framework.routers import DefaultRouter

from classroom import views

router = DefaultRouter()
router.register("classrooms", views.ClassroomViewSet, basename="classroom")

urlpatterns = [path("", include(router.urls))]
