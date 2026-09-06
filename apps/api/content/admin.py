from django.contrib import admin

from content.models import Article, ArticleProblemLink, Roadmap, RoadmapStep


class ArticleProblemLinkInline(admin.TabularInline):
    model = ArticleProblemLink
    extra = 1
    autocomplete_fields = ("problem",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "difficulty", "locale", "is_published", "published_at")
    list_filter = ("is_published", "locale", "topics")
    search_fields = ("slug", "title")
    filter_horizontal = ("topics",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("published_at", "created_at", "updated_at")
    inlines = [ArticleProblemLinkInline]


class RoadmapStepInline(admin.TabularInline):
    model = RoadmapStep
    extra = 1
    autocomplete_fields = ("article", "problem")


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "locale", "is_published", "order")
    list_filter = ("is_published", "locale")
    search_fields = ("slug", "title")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [RoadmapStepInline]
