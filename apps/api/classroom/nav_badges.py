"""Assignments not finished yet (see `core.nav_badges`)."""

from classroom.services import pending_assignments
from core.nav_badges import Badge, register

register(Badge(section="classroom", kind="todo", count=pending_assignments))
