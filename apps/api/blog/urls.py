from django.urls import include, path
from rest_framework.routers import DefaultRouter

from blog import views
from blog.staff_views import StaffPostViewSet

router = DefaultRouter()
router.register("posts", views.PostViewSet, basename="post")
router.register("staff/posts", StaffPostViewSet, basename="staff-post")

urlpatterns = [path("", include(router.urls))]
