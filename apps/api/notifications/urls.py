from django.urls import include, path
from rest_framework.routers import DefaultRouter

from notifications import views

router = DefaultRouter()
router.register("notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [
    # Before the router: its detail route would read "unsubscribe" as a pk.
    path(
        "notifications/unsubscribe/",
        views.EmailUnsubscribeView.as_view(),
        name="notification-email-unsubscribe",
    ),
    path("", include(router.urls)),
]
