"""The Uzbek Latin alphabet, old and new (ADR-0059).

Law O'RQ-1184 of 21.10.2026 (in force from 22.04.2027) rewrites the
alphabet: ``oʻ → ö``, ``gʻ → ğ``, ``sh → ş``, ``ch → ç``, and the tutuq
belgisi is ``ʼ``. Text written in the old form stays valid, so the platform
holds both. This module is the twin of ``packages/shared/src/alphabet.ts``:
one set of cases (``packages/shared/src/alphabet-cases.json``) checks both.

Never converted: code (fenced and inline), LaTeX, URLs, e-mail addresses,
file names, placeholders (``{count}``), HTML tags, link targets, and words
that are not Uzbek — camel case (``GitHub``), a short acronym (``SSH``),
letters Uzbek does not use (``w``, a ``c`` outside ``ch``, ``oo``, ``th``),
or a word from ``FOREIGN_WORDS`` (``Shift``). The conversion is a starting
point: staff correct what it misses.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from itertools import pairwise

#: Characters the old alphabet writes its apostrophe with.
OLD_APOSTROPHES = "'’ʻ‘`´"
#: The tutuq belgisi of the new alphabet (U+02BC).
TUTUQ = "ʼ"
#: The ``ʻ`` of ``oʻ`` and ``gʻ`` when the old alphabet is written back.
_TURNED_COMMA = "ʻ"

#: Words that look Uzbek to the letter rules but are not. Lower case.
FOREIGN_WORDS = frozenset(
    {
        "bash",
        "branch",
        "chart",
        "chrome",
        "crash",
        "dashboard",
        "english",
        "finish",
        "flash",
        "flush",
        "fresh",
        "hash",
        "publish",
        "push",
        "refresh",
        "sha",
        "shell",
        "shift",
        "shortcut",
        "ssh",
    }
)

#: Stems of foreign words that take Uzbek suffixes (``Changelogda``). Long
#: enough not to start an Uzbek word. Lower case.
FOREIGN_STEMS = ("challenge", "changelog", "dashboard", "shimmer")

_LETTER = "A-Za-zÀ-ɏ"
_APOS = "'’ʻ‘`´ʼ"

_PROTECTED = re.compile(
    "|".join(
        [
            r"```[\s\S]*?```",
            r"~~~[\s\S]*?~~~",
            r"(?<![A-Za-z])`[^`\n]+`",
            r"\$\$[\s\S]*?\$\$",
            r"\$[^$\n]+\$",
            r"\\\([\s\S]*?\\\)",
            r"\\\[[\s\S]*?\\\]",
            r"(?:https?://|www\.)[^\s<>()]+",
            r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
            r"\]\([^)\n]*\)",
            r"<[^<>\n]+>",
            r"\{[A-Za-z_][\w.]*\}",
            # A file name's extension is lower case: `Main.java`, not the
            # `yechildi.Shu` of a missing space.
            r"\b[\w-]+\.[a-z][a-z0-9]{0,4}\b",
        ]
    ),
    re.ASCII,
)

_WORD = re.compile(f"[{_LETTER}]+(?:[{_APOS}][{_LETTER}]+)*[{_APOS}]?")
_APOS_RE = re.compile(f"[{_APOS}]")
_FOREIGN_LETTERS = re.compile(r"w|c|oo|ee|th")
_NOT_UZBEK = re.compile(r"[^a-zöğşç]")
_NOT_UZBEK_NEW = re.compile(r"[^a-zöğşçʼ'’ʻ‘`´]")


def is_foreign_word(word: str) -> bool:
    """Whether a word is left as it is written (see the module docstring)."""
    bare = _APOS_RE.sub("", word)
    lower = bare.lower()
    if lower in FOREIGN_WORDS or lower.startswith(FOREIGN_STEMS):
        return True
    # A lower-to-upper step inside a word: GitHub, TypeScript, ChatGPT.
    if any(a.islower() and b.isupper() for a, b in pairwise(bare)):
        return True
    # A short all-caps word is an acronym: SSH, SHA, CPU.
    if 1 < len(bare) <= 4 and bare == bare.upper():
        return True
    # Letters are judged on the new spelling: `Qo'oq` is `qöoq`, not
    # `qooq`, and every Uzbek `c` has become `ç`.
    letters = _APOS_RE.sub("", _word_to_new(word)).lower()
    if _FOREIGN_LETTERS.search(letters):
        return True
    # A letter Uzbek does not use (ü, ı, â, é, …) — Turkish, French, German.
    return bool(_NOT_UZBEK.search(letters))


def _word_to_new(word: str) -> str:
    out: list[str] = []
    i = 0
    n = len(word)
    while i < n:
        char = word[i]
        nxt = word[i + 1] if i + 1 < n else ""
        lower = char.lower()
        if lower in ("o", "g") and nxt and nxt in OLD_APOSTROPHES:
            letter = "ö" if lower == "o" else "ğ"
            out.append(letter if char == lower else letter.upper())
            i += 2
        elif lower in ("s", "c") and nxt.lower() == "h":
            letter = "ş" if lower == "s" else "ç"
            out.append(letter if char == lower else letter.upper())
            i += 2
        elif (
            lower == "s"
            and nxt
            and nxt in OLD_APOSTROPHES
            and i + 2 < n
            and word[i + 2].lower() == "h"
        ):
            # ``s'h`` keeps two letters apart in the old alphabet (Is'hoq);
            # the new one has ``ş``, so a plain ``sh`` is two letters already.
            out.append(char)
            i += 2
        elif char in OLD_APOSTROPHES and 0 < i < n - 1:
            out.append(TUTUQ)
            i += 1
        else:
            out.append(char)
            i += 1
    return "".join(out)


def _word_to_old(word: str) -> str:
    caps = len(word) > 1 and word == word.upper()
    table = {
        "ö": "o" + _TURNED_COMMA,
        "Ö": "O" + _TURNED_COMMA,
        "ğ": "g" + _TURNED_COMMA,
        "Ğ": "G" + _TURNED_COMMA,
        "ş": "sh",
        "Ş": "SH" if caps else "Sh",
        "ç": "ch",
        "Ç": "CH" if caps else "Ch",
    }
    return "".join(table.get(char, char) for char in word)


def _convert(text: str, word: Callable[[str], str], skip: Callable[[str], bool]) -> str:
    def plain(part: str) -> str:
        return _WORD.sub(lambda m: m.group(0) if skip(m.group(0)) else word(m.group(0)), part)

    out: list[str] = []
    cursor = 0
    for match in _PROTECTED.finditer(text):
        out.append(plain(text[cursor : match.start()]))
        out.append(match.group(0))
        cursor = match.end()
    out.append(plain(text[cursor:]))
    return "".join(out)


def to_new_alphabet(text: str) -> str:
    """Old Uzbek Latin → the alphabet of O'RQ-1184."""
    return _convert(text, _word_to_new, is_foreign_word)


def to_old_alphabet(text: str) -> str:
    """The new alphabet → old Uzbek Latin (``oʻ``, ``gʻ`` with U+02BB)."""
    # Only letters outside Uzbek (ü, é, …) keep a word as it is here.
    return _convert(text, _word_to_old, lambda w: bool(_NOT_UZBEK_NEW.search(w.lower())))


def for_alphabet(text: str, alphabet: str) -> str:
    """Uzbek ``text`` in ``alphabet`` (``"new"`` or ``"old"``)."""
    if not text:
        return text
    return to_old_alphabet(text) if alphabet == "old" else to_new_alphabet(text)


def for_user(text: str, user: object, lang: str | None = "uz") -> str:
    """Text the server writes to ``user`` — mail, Telegram, a certificate.

    Only Uzbek text is touched (``lang`` is the TEXT's language, not the
    interface's), and only text the platform wrote: what a person typed —
    a name, a judge's feedback — stays as written.
    """
    if lang != "uz":
        return text
    return for_alphabet(text, getattr(user, "alphabet", "new") or "new")
