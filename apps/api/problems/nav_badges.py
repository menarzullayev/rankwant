"""New problems in the side menu (see `core.nav_badges`)."""

from datetime import datetime

from django.db.models import Min

from core.nav_badges import Badge, register
from problems.models import Problem


def published_since(since: datetime) -> int:
    # `Problem` records no publication date of its own; the first revision
    # that went public does. A problem made public without a revision (an
    # import) is therefore never "new" - it is left out rather than guessed.
    return (
        Problem.objects.filter(is_public=True)
        .annotate(first_published=Min("revisions__published_at"))
        .filter(first_published__gt=since)
        .count()
    )


register(Badge(section="problems", kind="new", count=published_since))
