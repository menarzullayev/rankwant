"""New quizzes in the side menu (see `core.nav_badges`)."""

from datetime import datetime

from core.nav_badges import Badge, register
from quizzes.models import Quiz


def created_since(since: datetime) -> int:
    # A quiz has no publication date; one written long ago and published
    # today is not counted. Creation is the only moment it records.
    return Quiz.objects.filter(is_published=True, created_at__gt=since).count()


register(Badge(section="quizzes", kind="new", count=created_since))
