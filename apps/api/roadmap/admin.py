from django.contrib import admin

from roadmap.models import RoadmapComment, RoadmapItem, RoadmapVote


class RoadmapCommentInline(admin.TabularInline):
    model = RoadmapComment
    extra = 0
    fields = ("author", "body", "is_hidden", "created_at")
    readonly_fields = ("created_at",)


@admin.register(RoadmapItem)
class RoadmapItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "target_quarter",
        "votes_count",
        "is_enabled",
        "released_at",
    )
    list_filter = ("status", "is_enabled", "target_quarter")
    search_fields = ("title", "body", "target_quarter")
    date_hierarchy = "created_at"
    autocomplete_fields = ("update",)
    readonly_fields = (
        "planned_at",
        "started_at",
        "released_at",
        "created_at",
        "updated_at",
    )
    inlines = [RoadmapCommentInline]

    @admin.display(description="Ovoz")
    def votes_count(self, obj: RoadmapItem) -> int:
        return obj.votes.count()


@admin.register(RoadmapVote)
class RoadmapVoteAdmin(admin.ModelAdmin):
    list_display = ("item", "user", "created_at")
    search_fields = ("user__username", "item__title")
    readonly_fields = ("created_at",)


@admin.register(RoadmapComment)
class RoadmapCommentAdmin(admin.ModelAdmin):
    list_display = ("item", "author", "is_hidden", "created_at")
    list_filter = ("is_hidden",)
    search_fields = ("body", "author__username", "item__title")
    readonly_fields = ("created_at", "updated_at")
