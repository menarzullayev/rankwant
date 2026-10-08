"""Arena rounds running now (see `core.nav_badges`)."""

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from arena.models import ArenaRound
from core.nav_badges import Badge, register

#: A round's end is its start plus a time per question, so it is not a
#: column to filter on. No round lasts this long; older ones are not read.
LONGEST_ROUND = timedelta(hours=6)


def running() -> int:
    now = timezone.now()
    rounds = ArenaRound.objects.filter(
        is_public=True, start_at__lte=now, start_at__gt=now - LONGEST_ROUND
    ).annotate(question_count=Count("items"))
    return sum(1 for item in rounds if item.is_running)


register(Badge(section="arena", kind="live", count=running))
