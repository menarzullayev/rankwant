from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("config.api_urls")),
]

# Ishlab chiqish quroli — productionda marshrut umuman qo'shilmaydi
# (settings.ADMIN_ENABLED izohiga qarang). Kerak bo'lsa: DJANGO_ADMIN=1.
if settings.ADMIN_ENABLED:
    urlpatterns.insert(0, path("admin/", admin.site.urls))
