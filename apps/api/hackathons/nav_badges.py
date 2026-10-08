"""Hackathons accepting work now (see `core.nav_badges`)."""

from django.utils import timezone

from core.nav_badges import Badge, register
from hackathons.models import Hackathon


def accepting() -> int:
    # Open until the submission deadline; the days until results are
    # announced are not "live" for a participant.
    now = timezone.now()
    return Hackathon.objects.filter(
        is_public=True, start_at__lte=now, submission_deadline__gt=now
    ).count()


register(Badge(section="hackathons", kind="live", count=accepting))
