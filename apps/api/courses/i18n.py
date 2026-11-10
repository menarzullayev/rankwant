"""Pick the translation a reader sees (ADR-0056 § 3.2).

Order: the reader's locale, then the course's base locale, then any locale
that exists. The chosen locale is returned with the row so the page can mark
a fallback openly (the `ContentName` pattern on the web), instead of showing
another language as if it were the reader's.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class _Translated(Protocol):
    locale: str


def pick[T: _Translated](rows: Iterable[T], locale: str, base_locale: str) -> T | None:
    by_locale = {row.locale: row for row in rows}
    if not by_locale:
        return None
    for code in (locale, base_locale):
        if code in by_locale:
            return by_locale[code]
    return by_locale[sorted(by_locale)[0]]
