"""Changelog entries in the site search (see `core.search`).

The canonical (Uzbek) entry and its translations are two sources: a
reader typing in Russian finds the Russian title, and the hit leads to
the same entry.
"""

from core.search import Source, register
from updates.models import SystemUpdate, SystemUpdateTranslation

register(
    Source(
        type="news",
        kind="update",
        queryset=lambda: SystemUpdate.objects.filter(
            status=SystemUpdate.Status.PUBLISHED, is_enabled=True
        ),
        primary="title",
        secondary=("body",),
        excerpt=("body",),
        order=("-released_at", "pk"),
        hit=lambda update: {
            "key": str(update.pk),
            "title": update.title,
            "date": update.released_at,
        },
    )
)

register(
    Source(
        type="news",
        kind="update_translation",
        queryset=lambda: SystemUpdateTranslation.objects.filter(
            update__status=SystemUpdate.Status.PUBLISHED, update__is_enabled=True
        ).select_related("update"),
        primary="title",
        order=("-update__released_at", "pk"),
        hit=lambda row: {
            "key": str(row.update_id),
            "title": row.title,
            "date": row.update.released_at,
        },
    )
)
