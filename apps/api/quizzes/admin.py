from django.contrib import admin

from quizzes.models import Choice, Question, Quiz, QuizAttempt, QuizQuestion


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "difficulty", "is_active")
    list_filter = ("is_active", "topics")
    search_fields = ("text",)
    inlines = [ChoiceInline]


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1
    autocomplete_fields = ("question",)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "is_published", "reward_qvant")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [QuizQuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "total", "qvant_awarded", "created_at")
    list_select_related = ("user", "quiz")
