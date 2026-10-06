"""Tournaments running now (see `core.nav_badges`)."""

from django.utils import timezone

from core.nav_badges import Badge, register
from tournaments.models import Tournament


def running() -> int:
    now = timezone.now()
    return Tournament.objects.filter(is_public=True, start_at__lte=now, end_at__gt=now).count()


register(Badge(section="tournaments", kind="live", count=running))
