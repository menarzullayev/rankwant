from django.contrib import admin

from . import models


class CourseTranslationInline(admin.StackedInline):
    model = models.CourseTranslation
    extra = 0


class ModuleInline(admin.TabularInline):
    model = models.Module
    extra = 0
    show_change_link = True


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("slug", "access", "level", "is_published", "review_requested_at", "order")
    list_filter = ("access", "level", "is_published")
    search_fields = ("slug", "translations__title")
    filter_horizontal = ("authors",)
    inlines = (CourseTranslationInline, ModuleInline)


class ModuleTranslationInline(admin.TabularInline):
    model = models.ModuleTranslation
    extra = 0


class SectionInline(admin.TabularInline):
    model = models.Section
    extra = 0
    show_change_link = True


@admin.register(models.Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("__str__", "course", "order", "reward_qvant")
    inlines = (ModuleTranslationInline, SectionInline)


class SectionTranslationInline(admin.TabularInline):
    model = models.SectionTranslation
    extra = 0


class LessonInline(admin.TabularInline):
    model = models.Lesson
    extra = 0
    show_change_link = True
    fields = ("order", "kind", "is_required", "is_preview")


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "module", "order")
    inlines = (SectionTranslationInline, LessonInline)


class LessonTranslationInline(admin.StackedInline):
    model = models.LessonTranslation
    extra = 0


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("__str__", "kind", "is_required", "is_preview", "video_provider")
    list_filter = ("kind", "video_provider")
    raw_id_fields = ("problem", "quiz")
    inlines = (LessonTranslationInline,)


@admin.register(models.Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "source", "created_at", "completed_at")
    list_filter = ("source",)
    raw_id_fields = ("user", "course")
