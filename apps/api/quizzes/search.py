"""Quiz in the site search (see `core.search`)."""

from core.search import Source, register
from quizzes.models import Quiz

register(
    Source(
        type="learn",
        kind="quiz",
        queryset=lambda: Quiz.objects.filter(is_published=True),
        primary="title",
        order=("-created_at", "pk"),
        hit=lambda row: {"key": row.slug, "title": row.title},
    )
)
