"""Unread posts in the side menu (see `core.nav_badges`)."""

from datetime import datetime

from blog.models import Post
from core.nav_badges import Badge, register


def published_since(since: datetime) -> int:
    return Post.objects.filter(is_published=True, published_at__gt=since).count()


register(Badge(section="blog", kind="unread", count=published_since))
