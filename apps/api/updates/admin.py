from django.contrib import admin

from updates.models import SystemUpdate, SystemUpdateTranslation, UpdateRead


class TranslationInline(admin.TabularInline):
    model = SystemUpdateTranslation
    extra = 0


@admin.register(SystemUpdate)
class SystemUpdateAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "module", "status", "is_enabled", "released_at", "version")
    list_filter = ("status", "kind", "module", "is_enabled")
    search_fields = ("title", "body", "version", "source_repo")
    date_hierarchy = "released_at"
    readonly_fields = ("published_at", "created_at", "updated_at")
    inlines = [TranslationInline]


@admin.register(UpdateRead)
class UpdateReadAdmin(admin.ModelAdmin):
    list_display = ("user", "update", "read_at")
    search_fields = ("user__username",)
    readonly_fields = ("read_at",)
