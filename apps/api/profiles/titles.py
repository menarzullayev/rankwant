"""Rating titles derived from the contests rating (ADR-0027).

Names live in the i18n catalogues (`title.<code>`) so a re-skin only
changes translations. This module owns the code, the lower bound and
the colour-group slot each tier belongs to.

Ladder (rating_contest -> code):
    0 -  599  quark        (grey / 0)
    600 - 899  atom         (grey / 1)
    900 - 1199  molecule    (grey / 2)
    1200 - 1299  droplet    (green / 0)
    1300 - 1399  meteorite  (green / 1)
    1400 - 1499  comet      (cyan / 0)
    1500 - 1599  moon       (cyan / 1)
    1600 - 1899  planet     (blue / 0)
    1900 - 2099  star       (violet / 0)
    2100 - 2299  supernova  (orange / 0)
    2300 - 2399  pulsar     (orange / 1)
    2400 - 2599  magnetar   (red / 0)
    2600 - 2999  black_hole (red / 1)
    3000 - 3199  galaxy     (red / 2)
    3200 - 3499  supercluster (red / 3)
    3500 +      cosmos      (red / 4)

A user without a rated contest (`rated_contest_count == 0`) has no
title - the starting 1200 is too cheap a signal.
"""

from __future__ import annotations

from typing import Any, TypedDict

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

#: (lower bound, code, colour group index). Sorted ascending by bound.
#: Tier number = index + 1. The colour group index is the nutella marker
#: count - black-leading characters on the rendered title.
TITLES: tuple[tuple[int, str, int], ...] = (
    (0, "quark", 0),
    (600, "atom", 1),
    (900, "molecule", 2),
    (1200, "droplet", 0),
    (1300, "meteorite", 1),
    (1400, "comet", 0),
    (1500, "moon", 1),
    (1600, "planet", 0),
    (1900, "star", 0),
    (2100, "supernova", 0),
    (2300, "pulsar", 1),
    (2400, "magnetar", 0),
    (2600, "black_hole", 1),
    (3000, "galaxy", 2),
    (3200, "supercluster", 3),
    (3500, "cosmos", 4),
)


#: Codeforces colour group each tier falls into. Drives --rw-rank-{group}
#: in apps/web/src/app/globals.css and the nutella marker.
COLOUR_GROUPS: tuple[str, ...] = (
    "grey",  # 1 quark
    "grey",  # 2 atom
    "grey",  # 3 molecule
    "green",  # 4 droplet
    "green",  # 5 meteorite
    "cyan",  # 6 comet
    "cyan",  # 7 moon
    "blue",  # 8 planet
    "violet",  # 9 star
    "orange",  # 10 supernova
    "orange",  # 11 pulsar
    "red",  # 12 magnetar
    "red",  # 13 black_hole
    "red",  # 14 galaxy
    "red",  # 15 supercluster
    "red",  # 16 cosmos
)


class Title(TypedDict):
    code: str
    level: int
    colour_group: str
    marker: int


def title_for(
    rating: int,
    rated_contests: int,
    has_imported_rating: bool = False,
) -> Title | None:
    """Return the title for `rating`, or None when the rating says nothing yet.

    A rating is meaningful in two cases:
    - the user has finished at least one rated contest here, or
    - the rating is imported from an external source (`has_imported_rating`,
      ADR-0026) - a real Codeforces rating is a real rating even before the
      first RankWant contest.

    Otherwise the starting 1200 says nothing about skill, so the user stays
    title-less (ADR-0018).
    """
    if rated_contests <= 0 and not has_imported_rating:
        return None
    tier_index = 0
    code_final = TITLES[0][1]
    marker_final = TITLES[0][2]
    for i, (floor, code, marker) in enumerate(TITLES):
        if rating >= floor:
            tier_index = i
            code_final = code
            marker_final = marker
    return {
        "code": code_final,
        "level": tier_index + 1,
        "colour_group": COLOUR_GROUPS[tier_index],
        "marker": marker_final,
    }


def colour_group(level: int) -> str:
    """CF colour group for a tier number (1..16)."""
    if level < 1:
        return COLOUR_GROUPS[0]
    if level > len(COLOUR_GROUPS):
        return COLOUR_GROUPS[-1]
    return COLOUR_GROUPS[level - 1]


def user_title(user: Any) -> Title | None:
    """Title for a user object.

    `rank_title` is the imported Codeforces tier (ADR-0026) - when it is
    set the rating came from Codeforces and is worth showing even though
    `rated_contest_count` is still zero.

    `rated_contest_count` itself stays reserved for the participation
    achievements (1 / 10 / 50 rated contests, ADR-0018) and is never
    back-filled here: doing so would grant those achievements to all
    974 498 imported users at once.
    """
    return title_for(
        user.rating_contest,
        user.rated_contest_count,
        has_imported_rating=bool(getattr(user, "rank_title", "")),
    )


def user_max_title(user: Any) -> Title | None:
    """Peak tier - computed from `max_rating_contest` (ADR-0027).

    `max_rating_contest` is maintained in two places: the Codeforces
    import (ADR-0026) and the contest rating service when a user's
    rating rises (`ratings/services.py`). So the peak is meaningful in
    exactly the same cases as the current title, and it uses the same
    guard - a brand-new user with no contests and no import has neither.

    Returns None when the peak is not recorded yet (nullable column).
    """
    peak = getattr(user, "max_rating_contest", None)
    if peak is None:
        return None
    return title_for(
        peak,
        user.rated_contest_count,
        has_imported_rating=bool(getattr(user, "rank_title", "")),
    )


def bands() -> list[dict[str, Any]]:
    """Rating chart boundaries - the last band has no upper bound."""
    result: list[dict[str, Any]] = []
    for i, (floor, code, marker) in enumerate(TITLES):
        result.append(
            {
                "code": code,
                "level": i + 1,
                "min": floor,
                "max": TITLES[i + 1][0] if i + 1 < len(TITLES) else None,
                "colour_group": COLOUR_GROUPS[i],
                "marker": marker,
            }
        )
    return result


class UserTitleSerializer(serializers.Serializer[Title]):
    code = serializers.CharField()
    level = serializers.IntegerField()
    colour_group = serializers.CharField()
    marker = serializers.IntegerField()


@extend_schema_field(UserTitleSerializer(allow_null=True))
class TitleField(serializers.Field):  # type: ignore[type-arg]
    """Title field - the colour of every username comes from this."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("source", "*")
        super().__init__(read_only=True, **kwargs)

    def to_representation(self, value: Any) -> Title | None:
        return user_title(value)
