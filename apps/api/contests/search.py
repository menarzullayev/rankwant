"""Contest in the site search (see `core.search`)."""

from contests.models import Contest
from core.search import Source, register

register(
    Source(
        type="contest",
        kind="contest",
        queryset=lambda: Contest.objects.filter(is_public=True),
        primary="title",
        secondary=("description",),
        excerpt=("description",),
        order=("-start_at", "pk"),
        hit=lambda row: {"key": row.slug, "title": row.title, "date": row.start_at},
    )
)
