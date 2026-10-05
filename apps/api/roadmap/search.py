"""The public product roadmap in the site search (see `core.search`)."""

from core.search import Source, register
from roadmap import services

register(
    Source(
        type="news",
        kind="plan",
        queryset=services.visible,
        primary="title",
        secondary=("body",),
        excerpt=("body",),
        order=("-created_at", "pk"),
        hit=lambda item: {"key": str(item.pk), "title": item.title, "date": item.created_at},
    )
)
