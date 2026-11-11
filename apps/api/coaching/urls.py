from django.urls import include, path
from rest_framework.routers import DefaultRouter

from coaching import views

router = DefaultRouter()
router.register("coaching", views.CoachingViewSet, basename="coaching")

urlpatterns = [path("", include(router.urls))]
