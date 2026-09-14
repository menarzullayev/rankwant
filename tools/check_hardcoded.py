"""Find user-facing strings in the admin panel that never go through t().

WHY THIS EXISTS
---------------
`tools/check_i18n.py` only walks code -> dictionary: it verifies that every
key the code asks for exists in all ten languages. It cannot see the
reverse direction, so a hardcoded `label: "Sana"` in a table header passes
it silently. The admin panel had **274** such strings while the checker
reported "toza ✓" and 86 `admin.label.*` keys sat unused in the
dictionaries.

`.tmp/scan_hardcoded.py` — the one-off scanner that produced the original
inventory — had a second blind spot that made its numbers untrustworthy
for exactly this class:

    if WIRED in text:
        continue        # skip any file that imports @/i18n/messages

38 of the 40 admin files import that module (for `title=` or an error
message) while still hardcoding every table header. So the scanner reported
2 admin files and 48 strings; `grep` found 18 files and 274. A partially
migrated file is the normal state during a migration, and it was the one
state the scanner could not see.

This checker does NOT skip wired files. That is the whole point.

RULES
-----
1. No prose literal in a rendered position inside admin files:
   `label:`, `title:`/`title=`, `help:`, `placeholder=`, `aria-label=`,
   `alt=`, JSX text, and string ternaries.
2. No `toLocaleDateString()` / `toLocaleString()` with no locale argument.
   The browser's locale is not the app's locale, so an admin reading the
   panel in Russian gets a date formatted for whatever the OS picked. Four
   instances of this were fixed by hand; this rule stops the fifth.

Widening the scope
------------------
The target list below covers the admin panel, which is where the migration
is unfinished. Once the content layer (`content/legal.ts`,
`lib/country-names.ts`, `lib/regions.ts`) is translated, `TARGETS` should
grow to the whole `apps/web/src`.

Usage
-----
    python tools/check_hardcoded.py      # exit 0 clean, exit 1 dirty
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web/src"

#: Where the check runs. See "Widening the scope" above.
TARGETS = (WEB / "components/admin", WEB / "app/admin")

SKIP_PARTS = {"node_modules", ".next", "__tests__"}


# --- "provably not prose" ---------------------------------------------------
#
# Recognising prose by vocabulary cannot be made complete: any allow-list of
# words is an admission that everything off the list is invisible. Position
# in the source, on the other hand, is decidable. So this checker flags
# every literal in a rendered position and rejects only what is provably
# code, a path, or a symbol.

#: A dotted lowerCamel key: `admin.label.text.date`.
KEYLIKE = re.compile(r"^[a-z][A-Za-z0-9]*(\.[a-zA-Z][A-Za-z0-9]*)+$")

#: A single identifier: camelCase, snake_case or SCREAMING_SNAKE. A bare
#: Capitalised word is NOT an identifier — it is a one-word label
#: ("Hammasi", "Faol", "Daraja"), and treating it as code silently drops
#: the shortest and most common UI strings.
IDENT = re.compile(
    r"^(?:"
    r"[a-z]+(?:[A-Z][A-Za-z0-9]*)+"
    r"|[a-z][a-z0-9]*(?:_[a-z0-9]+)+"
    r"|[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+"
    r"|[a-z]{2,}"
    r")$"
)

#: Paths, urls, route templates. Must match the WHOLE string: an unanchored
#: `\w+/\w+` let "Ramka/cover fayliga havola" pass as a path because it
#: merely contains a slash.
#:
#: ⚠️ The slug form requires a first segment of **two or more** characters.
#: With `+` it also swallowed `s/savol` — real Uzbek UI text ("seconds per
#: question") that happens to contain a slash. A false negative in the
#: checker is worse than a false positive: it hides the string forever.
PATHY = re.compile(
    r"^(?:"
    r"https?://\S*"
    r"|/\S*"
    r"|\./\S*"
    r"|@/\S*"
    r"|[\w.-]+\.(?:tsx?|jsx?|json|css|svg|png|jpe?g|webp|avif|woff2?|md|ya?ml|txt|py|sh|go|toml|lock)$"
    r"|[a-z0-9-]{2,}(?:/[a-z0-9-]+)+"
    r")$"
)

#: A regular-expression literal passed to `new RegExp(...)` or `pattern=`.
#: `[a-z0-9_-]+` is code, not prose — but it has letters, so every
#: shape-based filter above lets it through.
REGEXY = re.compile(r"^[\w\\\[\](){}|^$.*+?\-]+$")

COLORY = re.compile(r"^(?:#|rgb|hsl|color\(|\d|var\(--)")

#: Tailwind / `rw-` utility token. Variant prefixes (`sm:`, `dark:`,
#: `group-hover/`) are part of the token; the stem is either dash-joined
#: (`gap-4`, `rw-radius-sm`) or a bare layout keyword (`flex`, `grid`).
TW_TOKEN = re.compile(
    r"^(?:[a-z-]+[:/])*"
    r"(?:"
    r"[a-z]+-[\w\-.\[\]%/()#:,]*"
    r"|(?:flex|grid|block|inline|hidden|contents|table|relative|absolute|"
    r"fixed|sticky|static|isolate|truncate|underline|italic|antialiased|"
    r"uppercase|lowercase|capitalize|resize|grow|shrink|border|shadow|"
    r"rounded|transition|transform|filter|backdrop)"
    r")$"
)

#: Route / query templates: `${a}/${b}`, `?x=y`, `foo=bar`.
#:
#: ⚠️ The structure characters are `$`, `{`, `=`, `?` — deliberately NOT
#: `/`. Including the slash made every slash-containing label look like a
#: template and silently swallowed `s/savol` ("seconds per question"), which
#: is real UI text. Real paths are already covered by `PATHY`.
TEMPLATE_PATH = re.compile(r"^[^\s]*[\$\{=&?][^\s]*$")

SORT_KEY = re.compile(r"^-?[a-z][a-z0-9_]*$")
CSS_VALUE = re.compile(r"^(?:clamp|calc|min|max|var|rgba?|hsla?)\(|^\(prefers-")
CSS_VAR = re.compile(r"^--[\w-]+$")
SVG_PATH = re.compile(r"^[Mm][\d\s.,-]")
ONLY_INTERP = re.compile(r"^[\s\W]*(?:\$\{[^}]*\}[\s\W]*)+$")
ALLCAPS = re.compile(r"^[A-Z][A-Z0-9_]{1,}$")

#: Values that are deliberately literal in every language: symbols,
#: international acronyms, and ISO language codes used as option labels.
#: These stay as literals in the source, so the checker must not chase them.
#:
#: The last three are not prose at all — they are API field names, slug
#: examples and language codes shown to staff. Translating an identifier
#: would make it wrong, so they are exempt rather than keyed.
ALLOWED_LITERALS = {
    "#",
    "ACM/ICPC",
    "IOI",
    "uz",
    "ru",
    "en",
    "cpp23",
    "—",
    "-",
    "·",
    "/",
    "?",
    # Rating field names, shown as a tooltip on the ratings column.
    "skills / contest / activity / challenges",
    # Example topic slugs, shown as a placeholder.
    "math, graphs",
}

#: A short list of unmistakable Uzbek stems. NOT used to decide "is this
#: prose" — only to protect a real string from the ALLCAPS filter above.
UZ_WORD = re.compile(
    r"(?i)(?<![a-z])(?:yo'q|kerak|uchun|yoki|bilan|hammasi|mavzu|masala|"
    r"sahifa|holat|nomi|narx|sabab|izoh|sana|kod|til|faol|jami)(?![a-z])"
)


def strip_interpolations(s: str) -> str:
    """Replace every `${...}` (nesting-aware) with a single space.

    Without this a multi-line class template such as

        `shrink-0 rw-radius-sm ${active ? "rw-accent-bg" : "rw-dim-2"}`

    tokenises into `shrink-0`, `rw-radius-sm`, `active`, `?`, … and the
    non-class tokens make the whole blob look like prose.
    """
    out: list[str] = []
    i, n = 0, len(s)
    while i < n:
        if s.startswith("${", i):
            depth = 1
            j = i + 2
            while j < n and depth:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    depth -= 1
                j += 1
            out.append(" ")
            i = j
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def is_class_string(s: str) -> bool:
    """True when the literal is a className / style blob, not prose."""
    stripped = strip_interpolations(s)
    tokens = stripped.split()
    if not tokens:
        return False
    return all(TW_TOKEN.match(t) for t in tokens)


def is_prose(s: str, *, code_tokens: bool = True) -> bool:
    """The single decision point: anything not provably code is prose.

    `code_tokens` — when True (the default), a bare lowercase word counts as
    an identifier, which is right for code positions (`type: "checkbox"`,
    `ordering: "slug"`). It is wrong for JSX **text**: `<Badge>faol</Badge>`
    has no quotes and no code shape, yet the lowercase filter dropped it, so
    every status badge in the admin panel was invisible to this checker.
    """
    t = s.strip()
    if len(t) < 2:
        return False
    if t in ALLOWED_LITERALS:
        return False
    if not any(ch.isalpha() for ch in t):
        return False
    if KEYLIKE.match(t):
        return False
    if code_tokens and (IDENT.match(t) or SORT_KEY.match(t)):
        return False
    if PATHY.match(t) or COLORY.match(t):
        return False
    if TEMPLATE_PATH.match(t) or SVG_PATH.match(t):
        return False
    if CSS_VALUE.match(t) or CSS_VAR.match(t):
        return False
    if REGEXY.match(t) and re.search(r"[\[\]()|^$*+?]", t):
        return False
    if ONLY_INTERP.match(t):
        return False
    if ALLCAPS.match(t) and not UZ_WORD.search(t):
        return False
    if is_class_string(t):
        return False
    return True


# --- literal scanner --------------------------------------------------------


def scan_strings(text: str):
    """Yield (start, end, quote, body) for every string literal."""
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "\"'`":
            q = c
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == q:
                    break
                if q != "`" and text[j] == "\n":
                    break
                j += 1
            if j < n and text[j] == q:
                yield (i, j + 1, q, text[i + 1 : j])
                i = j + 1
                continue
        i += 1


#: Rendered object keys and JSX attributes whose value the user reads.
NAMED_POSITION = re.compile(
    r"\b(label|title|help|placeholder|alt|aria-label|aria-description)"
    r"\s*[:=]\s*$"
)
ATTR_POSITION = re.compile(r"\b(placeholder|alt|aria-label|aria-description)\s*=\s*$")


def classify(text: str, start: int) -> str | None:
    """Return the rendered position of the literal, or None if not rendered."""
    head = text[max(0, start - 160) : start]
    m = NAMED_POSITION.search(head)
    if m:
        return m.group(1)
    k = start - 1
    while k >= 0 and text[k] in " \t":
        k -= 1
    if k < 0:
        return None
    ch = text[k]
    if ch == ">":
        return "jsx-text"
    if ch == "?":
        return "ternary"
    if ch == "{":
        return "jsx-expr"
    return None


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


#: `toLocaleDateString()` / `toLocaleString()` with nothing between the
#: parens — the browser picks the locale, not the app.
NO_LOCALE_CALL = re.compile(r"\.toLocale(?:Date|Time)?String\(\s*\)")

#: JSX text content: `>some text<`.
#:
#: ⚠️ This is a SEPARATE rule because `scan_strings` only yields *quoted*
#: literals. JSX text has no quotes at all, so
#:
#:     <Badge color="success">faol</Badge>
#:
#: was completely invisible — not filtered, not reported. Every lowercase
#: status badge in the admin panel hid behind that hole. A checker that
#: cannot see a whole class of strings is the failure mode this file exists
#: to prevent, so the hole is closed rather than documented.
JSX_TEXT = re.compile(r">\s*([^<>{}]+?)\s*<")

#: JSX text that is only punctuation/whitespace carries nothing to translate.
JSX_TEXT_NOISE = re.compile(r"^[\s.,;:!?·—–\-/|&()\[\]]*$")

#: `>` and `<` are also comparison operators, so `>text<` matches ordinary
#: code: `Promise.all(x)`, `(30);`, `f.type === "checkbox" ? (`. A real JSX
#: text node never contains a paren, a semicolon or an equals sign.
JSX_TEXT_CODEISH = re.compile(r"[();=]")

#: A bare PascalCase token is a type or component name, not a label.
PASCAL_TOKEN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")


def target_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for target in TARGETS:
        if not target.exists():
            continue
        files += [
            p
            for p in sorted(list(target.rglob("*.tsx")) + list(target.rglob("*.ts")))
            if not any(part in SKIP_PARTS for part in p.parts)
        ]
    return files


def check_file(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")

    # Module specifiers are paths by definition — drop them explicitly.
    import_spans = [
        (m.start(), m.end())
        for m in re.finditer(r"\b(?:import|require|from)\b[^;\n]*", text)
    ]

    def in_import(pos: int) -> bool:
        return any(a <= pos < b for a, b in import_spans)

    problems: list[str] = []
    for start, _end, _q, body in scan_strings(text):
        if in_import(start):
            continue
        position = classify(text, start)
        if position is None:
            continue
        if not is_prose(body):
            continue
        problems.append(
            f"{rel}:{line_of(text, start)} [{position}] {body.strip()}"
        )

    for m in NO_LOCALE_CALL.finditer(text):
        problems.append(
            f"{rel}:{line_of(text, m.start())} [locale-less date] "
            f"{m.group(0)} — pass the active locale"
        )

    for m in JSX_TEXT.finditer(text):
        body = m.group(1).strip()
        if JSX_TEXT_NOISE.match(body):
            continue
        if JSX_TEXT_CODEISH.search(body):
            continue
        if PASCAL_TOKEN.match(body):
            continue
        if not is_prose(body, code_tokens=False):
            continue
        problems.append(
            f"{rel}:{line_of(text, m.start(1))} [jsx-text] {body}"
        )
    return problems


def main() -> int:
    problems: list[str] = []
    files = target_files()
    for path in files:
        problems += check_file(path)

    if problems:
        print("Qattiq yozilgan matn topildi (admin panelda `t()` dan o'tmagan):")
        for row in problems:
            print(f"  {row}")
        print(f"\nJami: {len(problems)} satr, {len(files)} fayl tekshirildi.")
        return 1

    print(f"Tekshirildi: {len(files)} admin fayl — qattiq yozilgan matn yo'q ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
