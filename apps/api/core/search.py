"""Site search — one engine, every app registers what it offers.

Before this module the header search queried four tables by hand, each
with its own idea of matching: problems went through a normalized
column, the other three through a raw `icontains`. Users were the worst
case — ~974k rows scanned with no index a `LIKE '%x%'` could use.

Now there is one place that decides how text is folded, how a match is
ranked and how a page is cut. An app describes a `Source` in its own
`search.py` (`core` must not import a feature app's models — see
`tools/check_architecture.py`) and `CoreConfig.ready()` discovers them.

Matching, in order:
  1. substring on the folded text, ranked exact > prefix > word start >
     anywhere > matched only in a secondary field;
  2. when a type has no substring match at all, trigram word similarity
     (PostgreSQL only) — the "algortm" → "Algoritm" case.

`large` sources (users) never take a full scan: a needle shorter than
three characters is a prefix match (the trigram index serves that; it
cannot serve a two-character substring) and they skip the fuzzy pass.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from django.db import connection
from django.db.models import (
    Case,
    Count,
    F,
    FloatField,
    Func,
    IntegerField,
    Q,
    QuerySet,
    TextField,
    Value,
    When,
    Window,
)

#: Uzbek Latin writes its apostrophe with several characters and imported
#: titles carry all of them. Search must not tell them apart: «yig'indi»
#: and «yigindi» are the same query.
APOSTROPHES = "'’ʻ‘`´"
_APOSTROPHE_RE = re.compile(f"[{re.escape(APOSTROPHES)}]")

#: Shortest needle worth a query, and the longest one accepted.
MIN_QUERY = 2
MAX_QUERY = 80

#: A needle shorter than this cannot use a trigram index for a substring.
TRIGRAM_MIN = 3
#: Typos are only guessed at for needles long enough to carry a signal.
FUZZY_MIN = 4
#: `word_similarity` floor. Measured: «algortm» against «algoritm» is 0.625.
FUZZY_FLOOR = 0.5

GROUP_LIMIT_DEFAULT = 4
GROUP_LIMIT_MAX = 10
PAGE_LIMIT_DEFAULT = 20
PAGE_LIMIT_MAX = 50
#: Deep pages are not a search use case and each one costs a larger sort.
OFFSET_MAX = 500

#: A large source is only asked when the needle carries at least this many
#: letters or digits. Measured on the live table (2026-10-06): `%%` and
#: `__` took 273 ms where an ordinary query takes 40–60 — punctuation
#: yields no trigram, so the index cannot narrow anything.
LARGE_MIN_ALNUM = 2

#: Rank of an exact lookup (a problem's number, typed as it is printed).
RANK_EXACT_LOOKUP = -1
#: Rank of a match found only in a secondary field (a summary, a body).
RANK_SECONDARY = 4
#: Characters of context kept on each side of a match inside a body.
SNIPPET_RADIUS = 48

#: Chips, in the order the palette shows them.
TYPES = ("problem", "user", "topic", "contest", "learn", "news", "shop")


def normalize_search(text: str) -> str:
    """Fold text for matching: no apostrophes, lower case, single spaces."""
    return " ".join(_APOSTROPHE_RE.sub("", text).lower().split())


def _sql_literal(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


#: The PostgreSQL form of `Fold`, shared with the migration that builds
#: the trigram indexes — an expression index is only used when the query
#: spells the expression the same way.
FOLD_PG = "LOWER(TRANSLATE({column}, " + _sql_literal(APOSTROPHES) + ", ''))"


class Fold(Func):
    """The database twin of `normalize_search` (it keeps repeated spaces)."""

    arity = 1
    output_field = TextField()

    def as_sql(  # type: ignore[override]
        self, compiler: Any, connection: Any, **extra: Any
    ) -> tuple[str, list[Any]]:
        inner, params = compiler.compile(self.source_expressions[0])
        if connection.vendor == "postgresql":
            return FOLD_PG.format(column=inner), list(params)
        # SQLite (local tests) has no TRANSLATE. Its LOWER is ASCII-only,
        # which is enough for the test data.
        sql = inner
        for char in APOSTROPHES:
            sql = f"REPLACE({sql}, {_sql_literal(char)}, '')"
        return f"LOWER({sql})", list(params)


@dataclass(frozen=True)
class Source:
    """One table's contribution to a result type."""

    #: Result type (a chip in the palette) — one of `TYPES`.
    type: str
    #: What the hit is within its type: `arena`, `quiz`, `update`, …
    kind: str
    queryset: Callable[[], QuerySet[Any]]
    #: The field a match is ranked on.
    primary: str
    #: Turns a row into `{key, title, …}`; the engine adds `type` and `kind`.
    hit: Callable[[Any], dict[str, Any]]
    #: Fields that may also match; such a match ranks last.
    secondary: tuple[str, ...] = ()
    #: `primary` already holds `normalize_search` output (a stored column).
    stored: bool = False
    #: Too large to scan — see the module docstring.
    large: bool = False
    #: Tie-break after the rank.
    order: tuple[str, ...] = ("pk",)
    #: A lookup that is not text matching: given the needle, a `Q` for the
    #: row it names outright (a problem by its number), or `None`.
    exact: Callable[[str], Q | None] | None = None
    #: Secondary fields long enough to be worth quoting from. A match found
    #: only there is shown with the sentence around it.
    excerpt: tuple[str, ...] = ()


_SOURCES: list[Source] = []


def register(source: Source) -> None:
    if source.type not in TYPES:
        raise ValueError(f"unknown search type: {source.type}")
    if any(s.type == source.type and s.kind == source.kind for s in _SOURCES):
        return  # a module imported twice (autoreload, tests)
    _SOURCES.append(source)


def sources(kind_of: str | None = None) -> list[Source]:
    return [s for s in _SOURCES if kind_of is None or s.type == kind_of]


def _expression(source: Source, field: str) -> Any:
    if source.stored and field == source.primary:
        return F(field)
    return Fold(field)


def _annotated(source: Source) -> tuple[QuerySet[Any], list[str]]:
    names = ["_s"] + [f"_s{i}" for i in range(len(source.secondary))]
    fields = (source.primary, *source.secondary)
    queryset = source.queryset().annotate(
        **{name: _expression(source, field) for name, field in zip(names, fields, strict=True)}
    )
    return queryset, names


def _condition(source: Source, names: Iterable[str], needle: str) -> Q:
    lookup = "startswith" if source.large and len(needle) < TRIGRAM_MIN else "contains"
    condition = Q()
    for name in names:
        condition |= Q(**{f"{name}__{lookup}": needle})
    return condition


def _askable(source: Source, needle: str) -> bool:
    """Whether this source can answer the needle without scanning itself."""
    if not source.large:
        return True
    return sum(char.isalnum() for char in needle) >= LARGE_MIN_ALNUM


def _matches(source: Source, needle: str) -> QuerySet[Any]:
    queryset, names = _annotated(source)
    condition = _condition(source, names, needle)
    lookup = source.exact(needle) if source.exact else None
    whens = []
    if lookup is not None:
        condition |= lookup
        whens.append(When(lookup, then=Value(RANK_EXACT_LOOKUP)))
    rank = Case(
        *whens,
        When(_s=needle, then=Value(0)),
        When(_s__startswith=needle, then=Value(1)),
        When(_s__contains=f" {needle}", then=Value(2)),
        When(_s__contains=needle, then=Value(3)),
        default=Value(RANK_SECONDARY),
        output_field=IntegerField(),
    )
    matched: QuerySet[Any] = (
        queryset.filter(condition)
        # The count rides on the page query. A separate `COUNT(*) … LIMIT`
        # was measured on a million users (2026-10-05): the planner
        # overestimates `LIKE '%abc%'`, picks a sequential scan for the
        # limited count and takes 320 ms where the page itself takes 19.
        .annotate(_rank=rank, _total=Window(Count("pk")))
        .order_by("_rank", *source.order)
    )
    return matched


def _fuzzy(source: Source, needle: str, limit: int) -> list[Any]:
    if connection.vendor != "postgresql" or source.large or len(needle) < FUZZY_MIN:
        return []
    queryset, _ = _annotated(source)
    similarity = Func(Value(needle), F("_s"), function="word_similarity", output_field=FloatField())
    return list(
        queryset.annotate(_sim=similarity)
        .filter(_sim__gte=FUZZY_FLOOR)
        .order_by("-_sim", *source.order)[:limit]
    )


def excerpt(text: str, needle: str) -> str:
    """The words around the first place `needle` occurs in `text`.

    Matching is done on the folded text, the cut on the original: the two
    differ in length wherever an apostrophe was dropped, so every folded
    character remembers where it came from.
    """
    folded: list[str] = []
    origin: list[int] = []
    for index, char in enumerate(text):
        if char in APOSTROPHES:
            continue
        for lowered in char.lower():
            folded.append(" " if lowered.isspace() else lowered)
            origin.append(index)
    at = "".join(folded).find(needle)
    if at < 0:
        return ""
    start = origin[at]
    end = origin[at + len(needle) - 1] + 1
    left = max(0, start - SNIPPET_RADIUS)
    right = min(len(text), end + SNIPPET_RADIUS)
    # Do not start or stop in the middle of a word.
    if left > 0:
        left = text.find(" ", left, start) + 1 or left
    if right < len(text):
        right = text.rfind(" ", end, right) if text.rfind(" ", end, right) > end else right
    body = " ".join(text[left:right].split())
    return ("…" if left > 0 else "") + body + ("…" if right < len(text) else "")


def _to_hit(source: Source, row: Any, needle: str = "") -> dict[str, Any]:
    hit = {"type": source.type, "kind": source.kind, **source.hit(row)}
    # Found only in a long text: say where, or the title alone would not
    # explain why this result is here.
    if needle and getattr(row, "_rank", None) == RANK_SECONDARY:
        for field in source.excerpt:
            quoted = excerpt(str(getattr(row, field, "") or ""), needle)
            if quoted:
                hit["snippet"] = quoted
                break
    return hit


def _group(kind_of: str, needle: str, limit: int, offset: int) -> dict[str, Any]:
    """One type's page: merged across its sources, rank first."""
    found = sources(kind_of)
    count = 0
    rows: list[tuple[int, int, int, Source, Any]] = []
    for index, source in enumerate(found):
        if not _askable(source, needle):
            continue
        matches = _matches(source, needle)
        page = list(matches[: offset + limit])
        # An offset past the end returns no row to read the total from.
        count += page[0]._total if page else (matches.count() if offset else 0)
        for position, row in enumerate(page):
            rows.append((row._rank, index, position, source, row))
    fuzzy = False
    if count == 0 and offset == 0:
        for index, source in enumerate(found):
            for position, row in enumerate(_fuzzy(source, needle, limit)):
                rows.append((round((1 - row._sim) * 1000), index, position, source, row))
        fuzzy = bool(rows)
        count = len(rows)
    rows.sort(key=lambda item: item[:3])
    # The one result the needle names outright — an exact lookup or an
    # exact title. Never a guess: a fuzzy group has no best.
    best = None
    if rows and not fuzzy and offset == 0 and rows[0][0] <= 0:
        best = _to_hit(rows[0][3], rows[0][4])
    return {
        "type": kind_of,
        "count": count,
        "fuzzy": fuzzy,
        "results": [
            _to_hit(source, row, needle) for _, _, _, source, row in rows[offset : offset + limit]
        ],
        "_best": best,
    }


def clamp(value: str | None, default: int, low: int, high: int) -> int:
    try:
        number = int(value) if value not in (None, "") else default
    except ValueError:
        number = default
    return max(low, min(high, number))


def search(
    query: str, kind_of: str = "all", limit: int | None = None, offset: int = 0
) -> dict[str, Any]:
    """Run a search.

    `kind_of="all"` returns the top few of every type that matched (the
    palette). A single type returns one page of it — and still the count
    of every other type, because the results page draws them on its tabs.
    """
    needle = normalize_search(query[:MAX_QUERY])
    single = kind_of in TYPES
    if limit is None:
        limit = PAGE_LIMIT_DEFAULT if single else GROUP_LIMIT_DEFAULT
    empty: dict[str, Any] = {
        "q": query.strip()[:MAX_QUERY],
        "type": kind_of if single else "all",
        "top": None,
        "groups": [],
        "counts": dict.fromkeys(TYPES, 0),
        "total": 0,
    }
    if len(needle) < MIN_QUERY:
        return empty
    groups = [
        _group(name, needle, limit, offset if name == kind_of else 0)
        if not single or name == kind_of
        # Another tab: only its count is needed, so ask for a single row.
        else _group(name, needle, 1, 0)
        for name in TYPES
    ]
    counts = {group["type"]: group["count"] for group in groups}
    shown = [g for g in groups if (g["type"] == kind_of if single else g["results"])]
    # In the order of `TYPES`: a problem's number beats a user who happens
    # to be called the same thing.
    top = next((g["_best"] for g in shown if g["_best"]), None)
    for group in groups:
        del group["_best"]
    return {**empty, "top": top, "groups": shown, "counts": counts, "total": sum(counts.values())}


def _users() -> QuerySet[Any]:
    from core.models import User

    return User.objects.filter(is_active=True)


register(
    Source(
        type="user",
        kind="user",
        queryset=_users,
        primary="username",
        secondary=("display_name",),
        large=True,
        order=("-rating_skills", "pk"),
        hit=lambda user: {
            "key": user.username,
            "title": user.username,
            "subtitle": user.display_name,
            "meta": user.rating_skills,
        },
    )
)
