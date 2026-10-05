from django.contrib import admin

from team.models import Department, Member, Role


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name_uz", "order")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("title_uz", "department", "badge", "order", "is_published")
    list_filter = ("department", "is_published")
    search_fields = ("title_uz", "title_en")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "title_uz", "holds_all_roles", "order", "is_published")
    list_filter = ("section", "is_published")
    search_fields = ("name",)
