"""Duel invitations waiting for an answer (see `core.nav_badges`)."""

from core.models import User
from core.nav_badges import Badge, register
from duels.models import Duel


def invitations(user: User) -> int:
    return Duel.objects.filter(opponent=user, status=Duel.Status.OPEN).count()


register(Badge(section="duels", kind="todo", count=invitations))
