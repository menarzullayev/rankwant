"""Changelog entries in the site search (see `core.search`).

Only the canonical (Uzbek) title is searched and shown: translations
live in their own table and the palette has no room for a join per key
stroke.
"""

from core.search import Source, register
from updates.models import SystemUpdate

register(
    Source(
        type="news",
        kind="update",
        queryset=lambda: SystemUpdate.objects.filter(
            status=SystemUpdate.Status.PUBLISHED, is_enabled=True
        ),
        primary="title",
        order=("-released_at", "pk"),
        hit=lambda update: {
            "key": str(update.pk),
            "title": update.title,
            "date": update.released_at,
        },
    )
)
