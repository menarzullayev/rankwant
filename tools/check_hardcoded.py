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

#: Files the check does not read.
#:
#: `i18n/` holds the dictionaries themselves — every string in them is
#: supposed to be there. The other three are the content layer: country and
#: region names, and the legal texts. They are translated as data, not
#: through `t()`, and were deliberately deferred to a separate task.
#:
#: `opengraph-image.tsx` is a different kind of exemption: it exports an
#: `ImageResponse` at module level, so it has no request scope and cannot
#: `await getLocale()`. Its strings are the brand plus a bare counter, and
#: the file says so in a comment. A key there would be unreachable.
SKIP_PARTS = {"node_modules", ".next", "__tests__"}
DEFERRED = (
    "content/legal.ts",
    "lib/country-names.ts",
    "lib/regions.ts",
    "opengraph-image.tsx",
)


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
    # A dotted host followed by a path: `github.com/owner/repo`. The host
    # form is specific enough not to swallow prose.
    r"|[\w-]+(?:\.[\w-]+)+/[\w./-]*"
    r")$"
)

#: A regular-expression literal passed to `new RegExp(...)` or `pattern=`.
#: `[a-z0-9_-]+` is code, not prose — but it has letters, so every
#: shape-based filter above lets it through.
REGEXY = re.compile(r"^[\w\\\[\](){}|^$.*+?\-]+$")

#: A colour value: `#fff`, `rgb(…)`, `hsl(…)`, `var(--x)`, `12px`.
#:
#: ⚠️ The bare `\d` that used to lead this alternation made EVERY string
#: starting with a digit a colour — so `"45 masala"` ("45 problems", real
#: UI text) was invisible. A digit only means a colour when it is a CSS
#: length or a unit-less number: `12px`, `0.5`, `1400`. Requiring the end of
#: the string after the number, or a CSS unit, is what closes the hole.
COLORY = re.compile(
    r"^(?:#|rgba?\(|hsla?\(|color\(|var\(--"
    r"|\d+(?:\.\d+)?(?:px|rem|em|vh|vw|%|deg|fr|s|ms)?$"
    r")"
)

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
CSS_VALUE = re.compile(r"^(?:clamp|calc|min|max|var|rgba?|hsla?|color-mix)\(|^\(prefers-")
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
    # Product names. The four rating categories are branded words, the same
    # way `Qvant` is the currency: a Russian user sees "Skills" by design,
    # and `leaderboard.skills` is already an explicit dictionary key.
    "RankWant", "Skills", "Contests", "Activity", "Challenges", "Qvant",
    # Browser and platform names in `describeAgent`. A translator passes
    # these through unchanged; only the separator between them is ours.
    "Edge", "Opera", "Yandex", "Firefox", "Chrome", "Safari",
    "iOS", "Android", "Windows", "macOS", "Linux",
    # A share title: the display name plus the product. The name is data,
    # the suffix is the brand, and only the separator is ours.
    "${name} · RankWant",
    # `alt` in an `opengraph-image.tsx` is a module-level export, not a
    # component: it cannot await the request locale. These keep the brand
    # name plus one noun — the honest state, not a translated one.
    "RankWant musobaqasi", "RankWant masalasi",
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
    # `/onboarding?welcome=1${next ? … : ""}` — a route template that spans
    # lines, so `TEMPLATE_PATH` cannot match it. Removing the interpolations
    # leaves the path itself, which is what decides.
    if "${" in t:
        remainder = strip_interpolations(t).strip()
        if not remainder or PATHY.match(remainder):
            return False
    # A template that starts with `/` is a route, whatever the
    # interpolations inside it: `/api/v1/auth/${p}/start/${next ? … : ""}`.
    # Removing the interpolations leaves `/api/v1/auth/ /start/`, which has
    # a space and so is not a path by shape — the leading slash decides.
    if "${" in t and t.startswith("/"):
        return False
    if CSS_VALUE.match(t) or CSS_VAR.match(t):
        return False
    if REGEXY.match(t) and re.search(r"[\[\]()|^$*+?]", t):
        return False
    if ONLY_INTERP.match(t):
        return False
    if is_number_with_unit(t):
        return False
    if KEYBOARD_SHORTCUT_TAIL.search(t):
        return False
    if GLYPH.match(t):
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
#: A number followed by a unit: `12 MB`, `1.5 KB`, `8 AC`, `30 px`.
#:
#: ⚠️ These were SIX false positives, and each one invites a bypass: a
#: checker that cries wolf gets `# noqa`-ed, and then it is dead. "AC" is a
#: verdict code from the API, "MB" is a unit, and neither is translated —
#: `attachments` in every dictionary shows "MB"/"KB" unchanged.
#:
#: The rule is deliberately narrow: it matches a TRAILING unit after a
#: number, in a string that is otherwise only interpolation and arithmetic.
#: `45 masala` ("45 problems") is prose and stays flagged — the unit list
#: holds only measurement symbols, never words.
NUMBER_UNIT = re.compile(
    r"^(?:.*?[\d)}])\s*(?:[KMGT]?B|AC|px|ms|s|%)[\s.,;)]*$"
)

#: A keyboard shortcut in parentheses: `Title (Ctrl+.)`.
#:
#: `Ctrl+.` names a physical key combination. It reads the same in all ten
#: languages, so keying it would mean ten identical values — and the tenth
#: would eventually drift.
KEYBOARD_SHORTCUT_TAIL = re.compile(
    r"\s*\(\s*(?:Ctrl|Cmd|Shift|Alt|Meta|⌘|⌥|⌃)[\s+]*[\w.+-]*\s*\)\s*$"
)

#: A bare glyph or punctuation cluster: `A−`, `→`, `←`, `·`.
#:
#: `A−` is the decrease-font button in `StatementSize`: an "A" plus a minus
#: sign, drawn the same way in every language. Its sibling carries a real
#: label (`aria-label={t(…, "problem.statementSizeDown")}`), so the glyph
#: needs no key of its own.
GLYPH = re.compile(r"^[A-Za-z]?[\s]*[−–—+\-×→←↑↓·°±≤≥≠~^]*$")


def is_number_with_unit(s: str) -> bool:
    """True for a measurement, not a sentence.

    The regex alone cannot tell "12 MB" from "45 masala": both are a number
    followed by a token. The unit list is the discriminator — every entry is
    a measurement symbol that appears verbatim in the dictionaries, so a
    string ending in one is a measurement regardless of what precedes it.
    """
    t = s.strip().rstrip(".,;)")
    return bool(NUMBER_UNIT.match(t))


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
    if ch == ":":
        # `:` is ambiguous: it introduces an object property AND the else
        # branch of a ternary. Treating every `:` as a branch flagged 250
        # object keys (`title: "title"`) as prose. A ternary's `:` has a
        # `?` before it, with no comma, brace or semicolon in between —
        # that is what separates `cond ? "a" : "b"` from `key: "value"`.
        head = text[max(0, start - 200) : start]
        mark = head.rfind("?")
        if mark >= 0 and not any(ch in head[mark:] for ch in ",;{}"):
            return "ternary-else"
        return None
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

#: `t()` called with a FIXED locale inside a client component.
#:
#: The server registers all ten dictionaries (`messages.server.ts`), but the
#: client receives only the active one. So `t(DEFAULT_LOCALE, …)` in a
#: `"use client"` file throws "dictionary is not registered" in every other
#: language — and because `t()` throws in dev, it takes the whole React tree
#: down with it. The page still answers 200 from the server, so only a
#: browser shows the damage.
#:
#: Seven such calls shipped: two in the header, which renders on every page,
#: and five in the admin. The header one made the app unusable in nine of the
#: ten languages while every check here stayed green.
HARDCODED_LOCALE_CALL = re.compile(
    r'\bt\(\s*(?:DEFAULT_LOCALE|"(?:uz|en|ru|kk|ky|tg|tr|zh|es|kaa)")'
)

#: JSX text that is only punctuation/whitespace carries nothing to translate.
JSX_TEXT_NOISE = re.compile(r"^[\s.,;:!?·—–\-/|&()\[\]`]*$")

#: `>` and `<` are also comparison operators, so `>text<` matches ordinary
#: code: `Promise.all(x)`, `(30);`, `f.type === "checkbox" ? (`. A real JSX
#: text node never contains a paren, a semicolon or an equals sign.
JSX_TEXT_CODEISH = re.compile(r"[();=]")

#: `viewBox={` — SVG geometry. The coordinates are numbers by definition, so
#: `0 0 ${W} ${H}` is not a label a translator could ever touch.
VIEWBOX_ATTR = re.compile(r"\bviewBox=\{\s*$")

#: A JSX text node that is really an arithmetic or SVG-coordinate fragment:
#: `0 && share`, `99 && share`.
#:
#: These come from the checker reading raw `>`…`<` spans, which in `.tsx`
#: are as often `<` (less-than) as a text node. Two digits joined by `&&`
#: carry no prose in any language.
JSX_TEXT_ARITHMETIC = re.compile(
    r"^[\s\d.${}A-Z()\[\]]*&{2}[\s\w.${}()\[\]]*$|^[\s\d.${}]+$"
)

#: HTML entities inside JSX text. `bo&apos;yicha` contains a semicolon, and
#: the code filter above read that semicolon as a statement separator — so
#: every Uzbek sentence with an apostrophe was silently skipped. Entities are
#: removed before the filter runs; the text itself is unaffected.
JSX_TEXT_ENTITY = re.compile(r"&[a-zA-Z]+;|&#\d+;")

#: A bare PascalCase token is a type or component name, not a label.
PASCAL_TOKEN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")

#: Lowercase tokens that are CODE, not prose, and that appear in exactly the
#: positions where the lowercase filter has to be switched off: Badge colours,
#: form-field discriminants, theme and style ids.
#:
#: `cond ? "ommaviy" : "yashirin"` is a label; `cond ? "success" : "warning"`
#: is a colour; `style === "clay" ? …` is a style id. All three are lowercase,
#: and only this list tells them apart. Kept explicit rather than inferred: a
#: new id means one line here, and that is a signal to look, not a nuisance.
CODE_TOKENS = {
    # Badge colours.
    "success", "error", "warning", "info", "brand", "neutral", "muted",
    "danger", "primary", "secondary",
    # Field discriminants.
    "text", "slug", "textarea", "number", "checkbox", "datetime", "select",
    "list", "left", "right",
    # Theme, style and effect ids — the same values `layout/styles.ts` uses
    # as keys. `light`/`dark`/`system` are theme modes, not words.
    "clay", "plain", "fade", "normal", "compact", "comfortable", "system",
    "light", "dark", "reduce", "big", "strong", "outline", "currentColor",
    "none",
    # `DifficultyBadge` level keys, mirrored from
    # `apps/api/problems/models.py`; they become `level-${level}` classes.
    "beginner", "basic", "intermediate", "upper", "hard", "expert", "master",
    # Routing and cache values.
    "page", "true", "false", "vs", "daily", "weekly", "ms", "getJson",
    "status", "polite", "busy", "idle", "network", "password", "login",
    "register", "draw", "contest", "difficulty",
    # Analytics event names, auth-flow keys and JSON-LD property names.
    "auth.register_done", "auth.login_done", "@id",
}


def client_files() -> list[pathlib.Path]:
    """Every `"use client"` file under `apps/web/src`.

    The fixed-locale rule below is not limited to the admin panel: the two
    calls that broke the most were in the header.
    """
    out: list[pathlib.Path] = []
    for suffix in (".tsx", ".ts"):
        for path in sorted(WEB.rglob(f"*{suffix}")):
            rel = str(path).replace("\\", "/")
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            if "/i18n/" in rel:
                continue
            if path.read_text(encoding="utf-8").startswith(('"use client"', "'use client'")):
                out.append(path)
    return out


def target_files() -> list[pathlib.Path]:
    """Every source file under `apps/web/src` whose prose is checked.

    ⚠️ This used to walk only `components/admin` and `app/admin`, because
    widening it earlier would have made the check fail for ~190 strings that
    were still to be translated — and a red gate is one that gets bypassed.
    The migration is finished, so the scope is now the whole tree.

    What stays out is `DEFERRED`: the content layer (`content/legal.ts`,
    `lib/country-names.ts`, `lib/regions.ts`), translated as data rather
    than through `t()`, and `opengraph-image.tsx`, whose `ImageResponse`
    export has no request scope and so cannot await the locale. The
    dictionaries themselves are skipped because every string in them is
    supposed to be there.

    The fixed-locale rule in `main()` covers every client file separately,
    because that defect is a crash rather than a missing translation.
    """
    out: list[pathlib.Path] = []
    for suffix in (".tsx", ".ts"):
        for path in sorted(WEB.rglob(f"*{suffix}")):
            rel = str(path).replace("\\", "/")
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            if "/i18n/" in rel:
                continue
            if any(rel.endswith(name) for name in DEFERRED):
                continue
            out.append(path)
    return out


#: `key={editing ? idOf(editing) : "new"}` — a React list key. It selects a
#: node, it is never rendered, so a sentinel like `"new"` is not a label.
REACT_KEY = re.compile(r"\bkey=\{[^{}]*$")


NEWLINE = chr(10)


def strip_comments(text: str) -> str:
    """Blank out `//` and `/* */` comments, keeping every offset in place.

    Offsets matter: the reported line number comes from the original text, so
    the replacement is spaces and newlines of the same length rather than a
    deletion.
    """
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        if text[i] == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find(NEWLINE, i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        if text[i] == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if text[k] != NEWLINE:
                    out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out)


def in_react_key(text: str, start: int) -> bool:
    return bool(REACT_KEY.search(text[max(0, start - 200) : start]))


#: `className={` / `class={` — a class expression. Whatever the string is,
#: the user never reads it, so `is_prose` has no business judging it. Four
#: class templates were reported as prose because a token like `group` is a
#: Tailwind utility but is not on the bare-keyword list.
CLASS_ATTR = re.compile(r"\b(?:class|className)=\{\s*$")


def in_class_attr(text: str, start: int) -> bool:
    return bool(CLASS_ATTR.search(text[max(0, start - 200) : start]))


def in_viewbox_attr(text: str, start: int) -> bool:
    return bool(VIEWBOX_ATTR.search(text[max(0, start - 200) : start]))


def check_file(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")

    #: `jsx-text` and `jsx-expr` are decided by the characters `>` and `{`,
    #: which exist in `.ts` too — as generic parameters, comparisons and
    #: object literals. Running those two rules on a plain `.ts` file
    #: produced 90 hits in `lib/api.ts`, every one of them a fragment of
    #: `Promise<…>` or `{ … }` rather than a string. JSX only exists in
    #: `.tsx`, so the two rules only run there.
    jsx = path.suffix == ".tsx"

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
        if in_react_key(text, start):
            continue
        if in_class_attr(text, start):
            continue
        if in_viewbox_attr(text, start):
            continue
        position = classify(text, start)
        if position is None:
            continue
        if not jsx and position in {"jsx-text", "jsx-expr"}:
            continue
        # Ternary branches hold prose as often as they hold a colour name,
        # so the lowercase filter comes off — with an explicit list of the
        # code tokens that legitimately appear there.
        loose = position in {"ternary", "ternary-else"}
        if body.strip() in CODE_TOKENS:
            continue
        if not is_prose(body, code_tokens=not loose):
            continue
        problems.append(
            f"{rel}:{line_of(text, start)} [{position}] {body.strip()}"
        )

    for m in NO_LOCALE_CALL.finditer(text):
        problems.append(
            f"{rel}:{line_of(text, m.start())} [locale-less date] "
            f"{m.group(0)} — pass the active locale"
        )

    # Raw JSX text nodes — `>some text<`. `.tsx` only, for the same reason
    # as above: in a `.ts` file every `>` is a generic or a comparison, and
    # this loop reported 90 fragments of `Promise<…>` in `lib/api.ts`.
    #
    # Comments come out first. `scan_strings` already skips them, but this
    # regex reads the raw text, and a JSDoc example like
    # `` * `Select` ichida ishlatiladi. */ `` matched as a text node.
    bare = strip_comments(text)
    for m in JSX_TEXT.finditer(bare) if jsx else ():
        body = m.group(1).strip()
        if JSX_TEXT_NOISE.match(body):
            continue
        if JSX_TEXT_CODEISH.search(JSX_TEXT_ENTITY.sub("", body)):
            continue
        if JSX_TEXT_ARITHMETIC.match(body):
            continue
        if PASCAL_TOKEN.match(body):
            continue
        if body in CODE_TOKENS:
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

    clients = client_files()
    for path in clients:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for match in HARDCODED_LOCALE_CALL.finditer(text):
            problems.append(
                f"{rel}:{line_of(text, match.start())} [fixed locale] "
                f"{match.group(0)} — use the active locale, not a constant"
            )

    if problems:
        print("Qattiq yozilgan matn topildi (`t()` dan o'tmagan):")
        for row in problems:
            print(f"  {row}")
        print(
            f"\nJami: {len(problems)} satr — "
            f"{len(files)} manba va {len(clients)} klient fayl tekshirildi."
        )
        return 1

    print(
        f"Tekshirildi: {len(files)} manba fayl + {len(clients)} klient fayl "
        f"— qattiq yozilgan matn yo'q ✓"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
