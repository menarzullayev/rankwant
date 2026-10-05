"""Hackathon in the site search (see `core.search`)."""

from core.search import Source, register
from hackathons.models import Hackathon

register(
    Source(
        type="contest",
        kind="hackathon",
        queryset=lambda: Hackathon.objects.filter(is_public=True),
        primary="title",
        secondary=("description",),
        excerpt=("description",),
        order=("-start_at", "pk"),
        hit=lambda row: {"key": row.slug, "title": row.title, "date": row.start_at},
    )
)
