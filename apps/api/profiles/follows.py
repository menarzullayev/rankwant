"""Who follows whom, for other apps (they may not read `profiles.models`)."""

from __future__ import annotations

from profiles.models import Follow


def follower_ids(user_id: int) -> list[int]:
    """People who follow this user."""
    return list(Follow.objects.filter(following_id=user_id).values_list("follower_id", flat=True))


def following_ids(user_id: int) -> list[int]:
    """People this user follows."""
    return list(Follow.objects.filter(follower_id=user_id).values_list("following_id", flat=True))
