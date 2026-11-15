"""Telling a new device from a returning one — for "new sign-in" notices.

A device is the browser family plus the operating system, not the whole agent
string: a browser update changes the version every few weeks and must not read
as a stranger.
"""

from __future__ import annotations

import hashlib
import logging
import re

from core.models import KnownDevice, User

log = logging.getLogger(__name__)

# Order matters: Edge and Opera also say "Chrome", Chrome also says "Safari".
_BROWSERS = (
    ("Edge", re.compile(r"Edg(e|A|iOS)?/")),
    ("Opera", re.compile(r"OPR/|Opera")),
    ("Firefox", re.compile(r"Firefox/|FxiOS/")),
    ("Chrome", re.compile(r"Chrome/|CriOS/")),
    ("Safari", re.compile(r"Safari/")),
)
_SYSTEMS = (
    ("Android", re.compile(r"Android")),
    ("iOS", re.compile(r"iPhone|iPad|iPod")),
    ("Windows", re.compile(r"Windows")),
    ("macOS", re.compile(r"Mac OS X|Macintosh")),
    ("Linux", re.compile(r"Linux|X11")),
)


def label(user_agent: str) -> str:
    """ "Chrome · Windows", or "" when the agent says nothing we can read."""
    browser = next((name for name, rx in _BROWSERS if rx.search(user_agent)), "")
    system = next((name for name, rx in _SYSTEMS if rx.search(user_agent)), "")
    return " · ".join(part for part in (browser, system) if part)


def note_sign_in(user: User, user_agent: str) -> None:
    """Remembers the device; warns the owner when it is a new one.

    The first device ever seen is recorded silently — it is the account's
    starting point, and every account that existed before this table was
    created starts the same way, so a deploy sends no wave of notices.
    Never raises: a sign-in must not fail on a notice.
    """
    try:
        name = label(user_agent)
        if not name:
            return
        key = hashlib.sha1(name.encode()).hexdigest()
        _, created = KnownDevice.objects.get_or_create(user=user, key=key, defaults={"label": name})
        if created and KnownDevice.objects.filter(user=user).count() > 1:
            from notifications import security

            security.new_device(user, name)
    except Exception:
        log.exception("yangi qurilma tekshiruvi yiqildi: %s", getattr(user, "pk", None))
