from django.contrib import admin

from classroom.models import Assignment, Classroom, ClassroomMember


class MemberInline(admin.TabularInline):
    model = ClassroomMember
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "owner", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("slug", "name", "owner__username")
    readonly_fields = ("join_code", "created_at")
    inlines = [MemberInline]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "classroom", "due_at", "created_at")
    filter_horizontal = ("problems",)
