from django.contrib import admin

from hackathons.models import Hackathon, HackathonSubmission


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "start_at", "submission_deadline", "end_at", "is_public")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(HackathonSubmission)
class HackathonSubmissionAdmin(admin.ModelAdmin):
    list_display = ("hackathon", "user", "title", "score", "scored_by", "submitted_at")
    list_filter = ("hackathon",)
    list_select_related = ("hackathon", "user", "scored_by")
