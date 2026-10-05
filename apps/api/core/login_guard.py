"""Limit on failed sign-ins: per client address and per account name.

Only FAILED attempts are counted. A scoped DRF throttle would count every
request, and a classroom behind one address signs in thirty times at the
start of a lesson — those are not guesses.

Two buckets, because they stop different attacks:

- address — one machine trying many accounts;
- account — many machines trying one account.

While a bucket is full the sign-in is refused before the password is
looked at: otherwise the limit would only slow the guessing down, the
right guess would still get through.

The account bucket is keyed by what was typed, not by a user row, so it
says nothing about whether the account exists (ADR-0015). Its price is
known: ten wrong attempts lock a name out for an hour, also for its
owner. Password reset stays open, and a successful sign-in is not
possible during the lock, so there is nothing to clear early.

If the guard's own cache calls fail it lets the request through and logs
it: the limit is a second line behind the password, not another way for
sign-in to break. (In a full cache outage the default DRF throttle already
refuses writes — see `core/throttling.py` — so nothing opens up there.)
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Any

from django.core.cache import cache
from rest_framework.settings import api_settings

from core.throttling import TrustedClientIdent

log = logging.getLogger(__name__)

SCOPE_IP = "login_ip"
SCOPE_ACCOUNT = "login_account"

_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def _rate(scope: str) -> tuple[int, int]:
    """`"20/hour"` → `(20, 3600)`. A missing or broken rate disables the bucket."""
    raw = str(api_settings.DEFAULT_THROTTLE_RATES.get(scope) or "")
    try:
        count, period = raw.split("/")
        return int(count), _SECONDS[period.strip()[0].lower()]
    except (ValueError, KeyError, IndexError):
        return 0, 0


def _buckets(request: Any, identifier: str) -> list[tuple[str, int, int]]:
    """`(cache key, limit, window)` for every bucket that applies."""
    found: list[tuple[str, int, int]] = []
    address = TrustedClientIdent().get_ident(request)
    limit, window = _rate(SCOPE_IP)
    if address and limit:
        found.append((f"login-fail:ip:{address}", limit, window))
    name = identifier.strip().casefold()
    limit, window = _rate(SCOPE_ACCOUNT)
    if name and limit:
        digest = hashlib.sha256(name.encode()).hexdigest()[:32]
        found.append((f"login-fail:id:{digest}", limit, window))
    return found


def retry_after(request: Any, identifier: str) -> int | None:
    """Seconds to wait if a bucket is full, else `None`."""
    try:
        wait = 0
        now = int(time.time())
        for key, limit, window in _buckets(request, identifier):
            if int(cache.get(key) or 0) >= limit:
                until = int(cache.get(f"{key}:until") or now + window)
                wait = max(wait, until - now, 1)
        return wait or None
    except Exception:
        log.warning("login guard: cache unavailable, sign-in not limited")
        return None


def record_failure(request: Any, identifier: str) -> None:
    try:
        now = int(time.time())
        for key, _limit, window in _buckets(request, identifier):
            # `add` starts the window; `incr` is atomic, so two failures at
            # once are both counted.
            if cache.add(key, 1, window):
                cache.set(f"{key}:until", now + window, window)
            else:
                try:
                    cache.incr(key)
                except ValueError:
                    # The key expired between `add` and `incr`.
                    cache.set(key, 1, window)
                    cache.set(f"{key}:until", now + window, window)
    except Exception:
        log.warning("login guard: cache unavailable, failure not counted")
