"""A problem statement as text a speech engine reads aloud in Uzbek (ADR-0064).

Formulas and numbers become words. Measured 2026-11-12: reading a statement with its formulas
as written gave 22.5 % character errors with the best voice, and 5.9 % once they were spoken
(three statements, the Uzbek Whisper judge of the 2026-10-14 benchmark). Statements are stored
in the old Latin alphabet, which is what the voice was trained on.

`spoken(parts)` is pure: the same statement always gives the same text, so the text's hash is
the audio's cache key.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from typing import Any, TypedDict


class Parts(TypedDict):
    title: str
    statement: str
    input_format: str
    output_format: str


ONES = ["nol", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
TENS = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]
SCALES = [
    (10**18, "kvintillion"),
    (10**15, "kvadrillion"),
    (10**12, "trillion"),
    (10**9, "milliard"),
    (10**6, "million"),
    (1000, "ming"),
]
LETTERS = {
    "a": "a",
    "b": "be",
    "c": "se",
    "d": "de",
    "e": "e",
    "f": "ef",
    "g": "ge",
    "h": "ha",
    "i": "i",
    "j": "je",
    "k": "ka",
    "l": "el",
    "m": "em",
    "n": "en",
    "o": "o",
    "p": "pe",
    "q": "qu",
    "r": "er",
    "s": "es",
    "t": "te",
    "u": "u",
    "v": "ve",
    "w": "dubl ve",
    "x": "iks",
    "y": "igrek",
    "z": "ze",
}
GREEK = {
    "alpha": "alfa",
    "beta": "beta",
    "gamma": "gamma",
    "delta": "delta",
    "epsilon": "epsilon",
    "varepsilon": "epsilon",
    "lambda": "lyambda",
    "mu": "myu",
    "pi": "pi",
    "sigma": "sigma",
    "phi": "fi",
    "varphi": "fi",
    "omega": "omega",
    "theta": "teta",
    "Delta": "delta",
    "Sigma": "sigma",
}
WORDS = {
    "\\le": "kichik yoki teng",
    "\\leq": "kichik yoki teng",
    "\\leqslant": "kichik yoki teng",
    "<=": "kichik yoki teng",
    "\\ge": "katta yoki teng",
    "\\geq": "katta yoki teng",
    "\\geqslant": "katta yoki teng",
    ">=": "katta yoki teng",
    "\\ne": "teng emas",
    "\\neq": "teng emas",
    "!=": "teng emas",
    "\\lt": "kichik",
    "\\gt": "katta",
    "<": "kichik",
    ">": "katta",
    "=": "teng",
    "\\approx": "taxminan teng",
    "+": "qo'shuv",
    "\\pm": "plyus minus",
    "*": "ko'paytuv",
    "\\cdot": "ko'paytuv",
    "\\times": "ko'paytuv",
    "/": "bo'luv",
    "\\div": "bo'luv",
    "mod": "modul",
    "\\bmod": "modul",
    "\\mod": "modul",
    "\\dots": "va hokazo",
    "\\ldots": "va hokazo",
    "\\cdots": "va hokazo",
    "\\infty": "cheksizlik",
    "\\in": "tegishli",
    "\\notin": "tegishli emas",
    "\\to": "dan",
    "\\rightarrow": "dan",
    "\\max": "maksimum",
    "\\min": "minimum",
    "\\log": "logarifm",
    "\\lg": "logarifm",
    "\\ln": "natural logarifm",
    "\\gcd": "EKUB",
    "\\operatorname{lcm}": "EKUK",
    "\\lcm": "EKUK",
    "\\sum": "yig'indi",
    "\\prod": "ko'paytma",
    "\\lfloor": "butun qismi",
    "\\lceil": "yuqoriga yaxlitlangani",
    "\\oplus": "XOR",
    "\\land": "va",
    "\\lor": "yoki",
    "\\neg": "emas",
    "\\forall": "har bir",
    "\\exists": "mavjud",
    "\\cup": "birlashma",
    "\\cap": "kesishma",
    "\\subset": "qism to'plami",
    "\\subseteq": "qism to'plami",
    "!": "faktorial",
    ",": ",",
    ";": ",",
    ".": ".",
    "|": "modul",
    "%": "foiz",
}
SILENT = {
    "\\;",
    "\\,",
    "\\!",
    "\\ ",
    "\\quad",
    "\\qquad",
    "(",
    ")",
    "[",
    "]",
    "\\left",
    "\\right",
    "\\{",
    "\\}",
    "\\rfloor",
    "\\rceil",
    "\\displaystyle",
    "\\limits",
    "&",
    "\\\\",
}
TOKEN = re.compile(
    r"@\d+@|\\[a-zA-Z]+|\\[;,! {}\\]"
    r"|[A-Za-z]+|\d+(?:\.\d+)?|\^\{[^{}]*\}|\^\S|_\{[^{}]*\}|_\S|<=|>=|!=|[-+*/=<>(),.;|!%&\[\]]"
)
#: Mathematical symbols typed straight into the text, outside any formula.
UNICODE_MATH = {
    "≤": "kichik yoki teng",
    "≥": "katta yoki teng",
    "≠": "teng emas",
    "∈": "tegishli",
    "×": "ko'paytuv",
    "·": "ko'paytuv",
    "−": "minus",
    "→": "dan",
    "∞": "cheksizlik",
}
#: A formula longer or deeper than this is said as one phrase: read symbol by symbol it
#: helps nobody (measured 2026-11-12: one statement nests four integrals in three fractions).
MAX_FORMULA = 400
MAX_GROUPS = 24
COMPLEX = "murakkab formula"
#: Commands whose argument is a brace group, read before the rest of the formula: their
#: groups nest (`\frac{n(n+1)}{2}`, `\frac{1}{\sqrt{n}}`), which a flat token cannot hold.
STRUCTURE = re.compile(
    r"\\(d?frac|sqrt|pmod|text|mathrm|textit|textbf|texttt|mathit|mathbf|operatorname)\s*(?=\{)"
)


def number(n: int) -> str:
    if n < 0:
        return "minus " + number(-n)
    if n < 10:
        return ONES[n]
    words: list[str] = []
    for value, name in SCALES:
        if n >= value:
            head, n = divmod(n, value)
            words.append(name if (head == 1 and name == "ming") else f"{number(head)} {name}")
    if n >= 100:
        head, n = divmod(n, 100)
        words.append("yuz" if head == 1 else f"{ONES[head]} yuz")
    if n >= 10:
        words.append(TENS[n // 10])
        n %= 10
    if n:
        words.append(ONES[n])
    return " ".join(words)


def decimal(text: str) -> str:
    whole, _, frac = text.partition(".")
    spoken = number(int(whole))
    if frac:
        spoken += " butun " + " ".join(ONES[int(d)] for d in frac)
    return spoken


def ordinal(n: int) -> str:
    word = number(n)
    return word + ("nchi" if word[-1] in "aeiou" else "inchi")


def letter(name: str) -> str:
    return LETTERS.get(name.lower(), name) if len(name) == 1 else name


def power(base: str, exp: str, said: list[str]) -> str:
    if exp == "2":
        return f"{base} kvadrat"
    if exp == "3":
        return f"{base} kub"
    if exp.isdigit():
        return f"{base}ning {ordinal(int(exp))} darajasi"
    return f"{base}ning {speak_math(exp, said)} darajasi"


def _group(expr: str, start: int) -> tuple[str, int]:
    """The brace group opening at `start`, nesting kept, and the index after it."""
    depth = 0
    for end in range(start, len(expr)):
        if expr[end] == "{":
            depth += 1
        elif expr[end] == "}":
            depth -= 1
            if depth == 0:
                return expr[start + 1 : end], end + 1
    return expr[start + 1 :], len(expr)


def _structures(expr: str, said: list[str]) -> str:
    """Speak every brace-argument command; leave `@k@` where it stood."""
    out: list[str] = []
    i = 0
    while i < len(expr):
        found = STRUCTURE.match(expr, i)
        if found is None:
            out.append(expr[i])
            i += 1
            continue
        name = found.group(1)
        first, i = _group(expr, found.end())
        if name.endswith("frac"):
            while i < len(expr) and expr[i] == " ":
                i += 1
            second, i = _group(expr, i) if i < len(expr) and expr[i] == "{" else ("", i)
            said.append(f"{speak_math(first, said)} bo'linib {speak_math(second, said)}")
        elif name == "sqrt":
            said.append(f"{speak_math(first, said)}ning ildizi")
        elif name == "pmod":
            said.append(f"modul {speak_math(first, said)}")
        elif name == "operatorname":
            said.append(WORDS.get(f"\\{first}", first))
        else:
            said.append(first)
        out.append(f" @{len(said) - 1}@ ")
    return "".join(out)


def speak_math(expr: str, said: list[str] | None = None) -> str:
    """One `$…$` formula as Uzbek words.

    `said` holds the spoken brace-argument commands of the formula this one is part of
    (`@k@` in the text); a nested part reads them from the same list.
    """
    if len(expr) > MAX_FORMULA or expr.count("{") > MAX_GROUPS:
        return COMPLEX
    # Markdown-escaped commands (`\\pmod`) are the commands themselves.
    expr = re.sub(r"\\\\(?=[A-Za-z])", r"\\", expr)
    expr = re.sub(r"\\[;,! ]|~", " ", expr).strip()
    tail = ""
    while expr and expr[-1] in ".,;":
        tail, expr = expr[-1] + tail, expr[:-1].rstrip()
    if tail:
        return speak_math(expr, said) + tail
    # `n(1 \le n \le 10^5)`: the name, then its range, which already says it.
    wrapped = re.fullmatch(r"([A-Za-z](?:_\{?\w+\}?)?)\s*\((.+)\)", expr)
    if wrapped and "\\le" in wrapped.group(2):
        return speak_math(wrapped.group(2), said)
    # A range, the most common shape in a statement: `L \le X \le R` → «X L dan R gacha».
    m = re.fullmatch(r"(.+?)\\leq?\s*(.+?)\s*\\leq?\s*(.+)", expr)
    if m and "\\le" not in m.group(3):
        low, middle, high = (speak_math(part, said) for part in m.groups())
        return f"{middle} {low}dan {high}gacha"
    out: list[str] = []
    said = said if said is not None else []
    tokens = TOKEN.findall(_structures(expr, said))
    skip = 0
    for i, tok in enumerate(tokens):
        if skip:
            skip -= 1
            continue
        if tok in SILENT:
            continue
        # `\sum_{i=1}^{n}`: the limits belong to the sum, not to a power.
        limits = (
            i + 2 < len(tokens) and tokens[i + 1].startswith("_") and tokens[i + 2].startswith("^")
        )
        if tok in ("\\sum", "\\prod") and limits:
            low = speak_math(tokens[i + 1][1:].strip("{}"), said)
            high = speak_math(tokens[i + 2][1:].strip("{}"), said)
            out.append(f"{low}dan {high}gacha {WORDS[tok]}")
            skip = 2
            continue
        if tok.startswith("^"):
            exp = tok[1:].strip("{}")
            base = out.pop() if out else ""
            out.append(power(base, exp, said))
        elif tok.startswith("_"):
            out.append(speak_math(tok[1:].strip("{}"), said))
        elif tok.startswith("@") and tok.endswith("@"):
            index = int(tok[1:-1])
            out.append(said[index] if index < len(said) else "")
        elif tok == "-":
            prev = tokens[i - 1] if i else ""
            out.append(
                "ayiruv" if prev and (prev[-1].isalnum() or prev in (")", "]", "}")) else "minus"
            )
        elif tok in WORDS:
            out.append(WORDS[tok])
        elif tok.startswith("\\") and tok[1:] in GREEK:
            out.append(GREEK[tok[1:]])
        elif tok.startswith("\\"):
            continue
        elif re.fullmatch(r"\d+(?:\.\d+)?", tok):
            out.append(decimal(tok))
        elif re.fullmatch(r"\d+[A-Za-z]", tok):
            out.append(f"{number(int(tok[:-1]))} {letter(tok[-1])}")
        elif len(tok) == 1:
            out.append(letter(tok))
        else:
            out.append(tok)
    text = " ".join(word for word in out if word)
    return re.sub(r"\s+([,.])", r"\1", text)


def _formula(expr: str) -> str:
    """A formula never fails the statement: a broken one is said as a phrase."""
    try:
        return speak_math(expr)
    except (RecursionError, IndexError, ValueError):
        return COMPLEX


def _markdown(text: str) -> str:
    """Markdown the ear does not need: code blocks, images, tables, links, emphasis."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s*\|?[-:\s|]+\|[-:\s|]*$", " ", text, flags=re.M)
    text = re.sub(r"\s*\|\s*", ", ", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text)
    text = re.sub(r"(?<![\w$])[*_](\S.*?)[*_](?!\w)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # `file\_server`, `possible_perm`: an identifier, read word by word.
    text = text.replace("\\_", "_")
    return re.sub(r"(?<=\w)_(?=\w)", " ", text)


def _apostrophes(text: str) -> str:
    """O' and g' as imported statements spell them: `o\\z`, ``Yo`nalish``, ʻ, ’ (2026-11-12)."""
    text = re.sub(r"(?<=[OoGg])(?:\\[`‘’ʻʼ']|[`‘’ʻʼ\\])(?=[A-Za-z])", "'", text)
    return re.sub(r"[‘’ʻʼ]", "'", text)


def _sentences(text: str) -> str:
    text = _apostrophes(text)
    # A short `x` or `a_i` in backticks is a name in the formula, read like one.
    text = re.sub(r"`([A-Za-z](?:_\w+)?|\d+)`", r"$\1$", text)
    # MathJax delimiters, as some imported statements write them: `\(…\)`, `\[…\]`, and the
    # Markdown-escaped `\\(…\\)`. Measured 2026-11-12: 2 625 backslashes were left unread.
    text = re.sub(r"\\{1,2}\[(.+?)\\{1,2}\]", r"$$\1$$", text, flags=re.S)
    text = re.sub(r"\\{1,2}\((.+?)\\{1,2}\)", r"$\1$", text, flags=re.S)
    text = re.sub(r"\$\$(.+?)\$\$", lambda m: " " + _formula(m.group(1)) + ". ", text, flags=re.S)
    # Brackets around a formula are punctuation to the eye, a stumble to the ear.
    text = re.sub(r"\(\s*(\$[^$]+\$)\s*\)", r", \1,", text)
    text = re.sub(r"\$([^$]+)\$", lambda m: " " + _formula(m.group(1)) + " ", text)
    text = _markdown(text)
    for symbol, word in UNICODE_MATH.items():
        text = text.replace(symbol, f" {word} ")
    text = re.sub(r"\b\d+(?:\.\d+)?\b", lambda m: decimal(m.group(0)), text)
    # What no rule above read must not reach the voice as «backslash» or «dollar».
    text = re.sub(r"[\\{}$^]", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"[,;]\s*\.", ".", text)
    text = re.sub(r"(?:,\s*){2,}", ", ", text)
    return re.sub(r"\s+", " ", text).strip(" ,")


def spoken(parts: Parts) -> str:
    """The whole statement in reading order: title, story, input, output."""
    chunks: list[str] = [_sentences(parts["title"]).rstrip(".") + "."]
    statement = parts["statement"] or ""
    heading = re.match(r"\s*#{1,6}\s+(.+?)\s*(?:\n|$)", statement)
    if heading and heading.group(1).strip().strip("*_`") == parts["title"].strip():
        statement = statement[heading.end() :]
    labelled: list[tuple[str, Callable[[], str]]] = [
        ("", lambda: statement),
        ("Kiruvchi ma'lumot.", lambda: parts["input_format"]),
        ("Chiquvchi ma'lumot.", lambda: parts["output_format"]),
    ]
    for label, read in labelled:
        body = _sentences(read() or "")
        if body:
            chunks.append(f"{label} {body}".strip())
    text = " ".join(chunk if chunk.endswith((".", "!", "?")) else chunk + "." for chunk in chunks)
    return re.sub(r"\s+", " ", text).strip()


def cache_key(model: str, text: str) -> str:
    """The audio's name: the same model reading the same text gives the same file."""
    return hashlib.sha256(f"{model}\n{text}".encode()).hexdigest()[:40]


def uzbek_parts(problem: Any) -> Parts | None:
    """The statement in Uzbek, the only language the voice reads: the author's text when it is
    Uzbek, else an Uzbek translation (ADR-0058); `None` when there is neither."""
    if problem.statement_locale == "uz":
        row: Any = problem
    else:
        row = problem.translations.filter(locale="uz").first()
        if row is None:
            return None
    return {
        "title": row.title or "",
        "statement": row.statement or "",
        "input_format": row.input_format or "",
        "output_format": row.output_format or "",
    }


#: The longest piece the voice reads in one go. A statement is read piece by
#: piece: the first listener hears the first piece while the rest are made,
#: and an edited sentence remakes only its own piece (ADR-0064 § 5).
SEGMENT_CHARS = 400
#: The first piece is short (~8 s on the GPU): it is what the first listener waits for, and
#: each next one may be a little longer (`SEGMENT_GROWTH`). Measured
#: 2026-11-12: 301 characters took 17.1 s for 20.5 s of audio (RTF 0.84).
#: Made one after another, piece k+1 is ready before piece k ends as long as
#: it is at most ~1.19× the audio already played — growing by 15 % keeps it
#: inside that; the first try packed a title alone (18 characters) before a
#: 384-character piece and left the listener ~20 s of silence.
FIRST_SEGMENT_CHARS = 120
SEGMENT_GROWTH = 1.15

_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


def _cap(index: int, first: int, limit: int) -> int:
    # The second piece is as short as the first: it is made while the first
    # plays, with the request and the upload on top (measured: growing it
    # already left a 1.1 s gap). Growth starts from the third.
    return min(limit, int(first * SEGMENT_GROWTH ** max(0, index - 1)))


def segments(text: str, limit: int = SEGMENT_CHARS, first: int = FIRST_SEGMENT_CHARS) -> list[str]:
    """Split the spoken text into pieces that grow from `first` to `limit` characters.

    Sentences are kept whole where they fit. A piece is closed at a sentence
    end once it is at least 60 % full; a sentence that does not fit an
    emptier piece is cut at its last comma or space so the piece fills up —
    no piece is left tiny before a long one.
    """
    pieces: list[str] = []
    current = ""
    queue = [part for part in _SENTENCE_END.split(text.strip()) if part]
    while queue:
        sentence = queue.pop(0)
        cap = _cap(len(pieces), first, limit)
        room = cap - (len(current) + 1 if current else 0)
        if len(sentence) <= room:
            current = f"{current} {sentence}".strip()
            continue
        if current and (len(current) >= cap * 0.6 or room < 20):
            pieces.append(current)
            current = ""
            queue.insert(0, sentence)
            continue
        cut = max(sentence.rfind(", ", 0, room), sentence.rfind(" ", 0, room))
        cut = cut if cut > room // 2 else room
        head, rest = sentence[: cut + 1].strip(), sentence[cut + 1 :].strip()
        pieces.append(f"{current} {head}".strip())
        current = ""
        if rest:
            queue.insert(0, rest)
    if current:
        pieces.append(current)
    return pieces
