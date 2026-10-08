"""Contests running now (see `core.nav_badges`)."""

from django.utils import timezone

from contests.models import Contest
from core.nav_badges import Badge, register


def running() -> int:
    now = timezone.now()
    return Contest.objects.filter(is_public=True, start_at__lte=now, end_at__gt=now).count()


register(Badge(section="contests", kind="live", count=running))
