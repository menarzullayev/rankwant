from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hacks import views

router = DefaultRouter()
router.register("hacks", views.HackViewSet, basename="hack")
router.register("hack-locks", views.HackLockViewSet, basename="hacklock")

urlpatterns = [path("", include(router.urls))]
