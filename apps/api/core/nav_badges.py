"""Side-menu badges — one request, every app says what it has.

The menu used to carry one number: unread changelog entries, with a
table row per entry read (`updates.UpdateRead`). That model does not
stretch to the other sections — a row per problem per user is 1 229
problems times every account — so a badge here is one of four kinds,
and only two of them store anything:

  todo    something waits for the user (an open duel invitation, an
          assignment not finished). Computed; it goes away when the work
          is done, not when the page is opened.
  live    something is running right now. The same for everyone, so it
          is computed once and cached for all.
  unread  entries published since the user last opened the section.
  new     the same, for reference content (problems, articles, quizzes).

`unread` and `new` keep a single watermark per user and section
(`NavSeen`), never a row per entry.

An app describes its badge in its own `nav_badges.py` (`core` must not
import a feature app's models — see `tools/check_architecture.py`) and
`CoreConfig.ready()` discovers them, as it does for `search.py`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Literal

from django.utils import timezone

from core.cache import cache_delete, cache_get, cache_set

if TYPE_CHECKING:
    from core.models import User

log = logging.getLogger(__name__)

Kind = Literal["todo", "live", "unread", "new"]

#: Nothing published before the feature shipped counts as unseen. Without
#: this every existing account would open the site to "99+" on each
#: section; the join date alone does not help an account from last year.
EPOCH = datetime(2026, 10, 6, tzinfo=UTC)

#: A user's badges are read on every navigation; the counts behind them
#: change far less often.
USER_CACHE_S = 60
#: What is running now is shared by every visitor.
LIVE_CACHE_S = 30
LIVE_CACHE_KEY = "nav-badges:live"


@dataclass(frozen=True)
class Badge:
    section: str
    kind: Kind
    #: `todo`: `count(user)`. `live`: `count()`. `unread` / `new`:
    #: `count(since)` — entries published after that moment.
    count: Callable[..., int]


_REGISTRY: dict[str, Badge] = {}


def register(badge: Badge) -> None:
    if badge.section in _REGISTRY:
        raise ValueError(f"nav badge registered twice: {badge.section}")
    _REGISTRY[badge.section] = badge


def sections(*kinds: Kind) -> list[str]:
    return sorted(s for s, b in _REGISTRY.items() if not kinds or b.kind in kinds)


def has_watermark(section: str) -> bool:
    badge = _REGISTRY.get(section)
    return badge is not None and badge.kind in ("unread", "new")


def _user_key(user_id: int) -> str:
    return f"nav-badges:user:{user_id}"


def _safe(badge: Badge, *args: object) -> int:
    """One section failing must not take the menu's other badges with it."""
    try:
        return max(0, int(badge.count(*args)))
    except Exception:
        log.exception("nav badge failed: %s", badge.section)
        return 0


def _live() -> dict[str, int]:
    cached = cache_get(LIVE_CACHE_KEY)
    if cached is not None:
        return dict(cached)
    counts = {b.section: _safe(b) for b in _REGISTRY.values() if b.kind == "live"}
    cache_set(LIVE_CACHE_KEY, counts, LIVE_CACHE_S)
    return counts


def _personal(user: User) -> dict[str, int]:
    from core.models import NavSeen

    cached = cache_get(_user_key(user.pk))
    if cached is not None:
        return dict(cached)
    seen = dict(NavSeen.objects.filter(user=user).values_list("section", "seen_at"))
    floor = max(EPOCH, user.date_joined)
    counts: dict[str, int] = {}
    for badge in _REGISTRY.values():
        if badge.kind == "todo":
            counts[badge.section] = _safe(badge, user)
        elif badge.kind in ("unread", "new"):
            counts[badge.section] = _safe(badge, max(floor, seen.get(badge.section, floor)))
    cache_set(_user_key(user.pk), counts, USER_CACHE_S)
    return counts


def badges_for(user: User) -> dict[str, dict[str, object]]:
    """Every badge that has something to show, keyed by section."""
    counts = {**_live(), **_personal(user)}
    return {
        section: {"kind": _REGISTRY[section].kind, "count": count}
        for section, count in sorted(counts.items())
        if count > 0 and section in _REGISTRY
    }


def mark_seen(user: User, section: str) -> None:
    """The user opened the section: what is there now is no longer new."""
    from core.models import NavSeen

    if not has_watermark(section):
        raise KeyError(section)
    NavSeen.objects.update_or_create(
        user=user, section=section, defaults={"seen_at": timezone.now()}
    )
    cache_delete(_user_key(user.pk))


__all__ = ["EPOCH", "Badge", "badges_for", "has_watermark", "mark_seen", "register", "sections"]
