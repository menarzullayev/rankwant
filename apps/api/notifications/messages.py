"""Notification wording on the server — for Telegram and for the stored fallback.

The site draws a coded notification from its own dictionaries, in the
language the reader is using right now. The server still needs words of
its own in two places: the message it hands to Telegram, and the
`title`/`body` kept on the row for anything that cannot look the code up
(an old client, a code that was later retired).

`message_catalog.py` is generated from the web dictionaries
(`tools/export_notification_messages.py`), so there is one place where a
sentence is written; CI fails when the two drift apart. It is a Python
module rather than a data file on purpose: `tools/check_deploy.sh`
compares the `.py` files of a running container with the source, and a
JSON file would change without the deploy noticing.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from django.utils import timezone

from notifications.message_catalog import CATALOG

_SLOT = re.compile(r"\{(\w+)\}")

#: Language every code is guaranteed to have.
SOURCE_LOCALE = "uz"


def codes() -> frozenset[str]:
    return frozenset(CATALOG.get(SOURCE_LOCALE, {}))


def _shown(key: str, value: Any) -> str:
    """A parameter as text. Keys ending in `_at` hold an ISO timestamp."""
    if key.endswith("_at") and isinstance(value, str):
        try:
            moment = datetime.fromisoformat(value)
        except ValueError:
            return value
        if timezone.is_naive(moment):
            moment = timezone.make_aware(moment)
        return f"{timezone.localtime(moment):%d.%m.%Y %H:%M}"
    return str(value)


def _fill(template: str, params: dict[str, Any]) -> str:
    return _SLOT.sub(
        lambda match: _shown(match[1], params[match[1]]) if match[1] in params else match[0],
        template,
    )


def render(code: str, params: dict[str, Any] | None, locale: str) -> tuple[str, str]:
    """`(title, body)` for a code, in `locale` or — failing that — in Uzbek."""
    entry = CATALOG.get(locale, {}).get(code) or CATALOG.get(SOURCE_LOCALE, {}).get(code)
    if not entry:
        return "", ""
    values = params or {}
    return _fill(entry.get("title", ""), values), _fill(entry.get("body", ""), values)
