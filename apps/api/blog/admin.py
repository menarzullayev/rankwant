from django.contrib import admin

from blog.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("slug", "kind", "title", "is_published", "published_at", "notified_at")
    list_filter = ("kind", "is_published", "locale")
    search_fields = ("slug", "title")
    readonly_fields = ("published_at", "notified_at", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
