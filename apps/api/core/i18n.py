"""Translate English property names. There is no fallback locale.

A missing string in `ru` is not replaced by Uzbek or English. The caller
sees the property itself (`user.name`, `email.subject`) so a gap is
visible instead of a silent lie.
"""

from __future__ import annotations

from collections.abc import Mapping


def translate(
    locale: str,
    *properties: str,
    catalog: Mapping[str, Mapping[str, str]],
) -> str | tuple[str, ...]:
    """Return the catalog text for each English property in `locale`.

    One property → that string. Several properties → a tuple, same
    order. An empty or missing entry is the property name itself.
    """
    texts: list[str] = []
    for property_name in properties:
        by_locale = catalog.get(property_name, {})
        text = by_locale.get(locale, "")
        if isinstance(text, str) and text.strip():
            texts.append(text)
        else:
            texts.append(property_name)
    if len(texts) == 1:
        return texts[0]
    return tuple(texts)
