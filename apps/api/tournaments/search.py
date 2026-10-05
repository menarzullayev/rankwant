"""Tournament in the site search (see `core.search`)."""

from core.search import Source, register
from tournaments.models import Tournament

register(
    Source(
        type="contest",
        kind="tournament",
        queryset=lambda: Tournament.objects.filter(is_public=True),
        primary="title",
        order=("-start_at", "pk"),
        hit=lambda row: {"key": row.slug, "title": row.title, "date": row.start_at},
    )
)
