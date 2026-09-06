from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hackathons import views

router = DefaultRouter()
router.register("hackathons", views.HackathonViewSet, basename="hackathon")

urlpatterns = [path("", include(router.urls))]
