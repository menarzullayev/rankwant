from django.urls import include, path
from rest_framework.routers import DefaultRouter

from contests import views
from contests.organizer_views import OrganizerContestViewSet
from contests.staff_views import StaffContestViewSet

router = DefaultRouter()
# `mine` OLDIN ro'yxatga olinadi: aks holda `contests/<slug>/` detali
# `contests/mine/` ni o'ziga yutib olib, POST 405 berardi.
router.register("contests/mine", OrganizerContestViewSet, basename="mine-contest")
router.register("contests", views.ContestViewSet, basename="contest")
router.register("staff/contests", StaffContestViewSet, basename="staff-contest")

urlpatterns = [
    path("", include(router.urls)),
    path("certificates/<uuid:pk>/", views.CertificateView.as_view(), name="certificate"),
    path(
        "certificates/<uuid:pk>/pdf/",
        views.CertificatePdfView.as_view(),
        name="certificate-pdf",
    ),
    path(
        "users/<str:username>/certificates/",
        views.UserCertificatesView.as_view(),
        name="user-certificates",
    ),
]
