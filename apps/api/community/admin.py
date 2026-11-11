from django.contrib import admin

from community.models import Comment, Report, Vote


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "target_type",
        "target_id",
        "author",
        "score",
        "report_count",
        "is_hidden",
    )
    list_filter = ("target_type", "is_hidden", "is_deleted")
    search_fields = ("body", "author__username")
    raw_id_fields = ("author", "parent", "root")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "object_id", "value", "author", "created_at")
    raw_id_fields = ("user", "author")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("kind", "object_id", "reason", "status", "reporter", "created_at")
    list_filter = ("status", "reason", "kind")
    raw_id_fields = ("reporter", "handled_by")
