"""New articles and algorithm notes in the side menu (see `core.nav_badges`)."""

from collections.abc import Callable
from datetime import datetime

from content.models import Article
from core.nav_badges import Badge, register


def published_since(kind: str) -> Callable[[datetime], int]:
    def count(since: datetime) -> int:
        return Article.objects.filter(kind=kind, is_published=True, published_at__gt=since).count()

    return count


register(Badge(section="learn", kind="new", count=published_since(Article.Kind.ARTICLE)))
register(Badge(section="algorithms", kind="new", count=published_since(Article.Kind.ALGORITHM)))
