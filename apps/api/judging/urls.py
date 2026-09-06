from django.urls import include, path
from rest_framework.routers import DefaultRouter

from judging import views

router = DefaultRouter()
router.register("attempts", views.AttemptViewSet, basename="attempt")

urlpatterns = [path("", include(router.urls))]
