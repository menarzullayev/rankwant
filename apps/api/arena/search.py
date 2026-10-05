"""ArenaRound in the site search (see `core.search`)."""

from arena.models import ArenaRound
from core.search import Source, register

register(
    Source(
        type="contest",
        kind="arena",
        queryset=lambda: ArenaRound.objects.filter(is_public=True),
        primary="title",
        order=("-start_at", "pk"),
        hit=lambda row: {"key": row.slug, "title": row.title, "date": row.start_at},
    )
)
