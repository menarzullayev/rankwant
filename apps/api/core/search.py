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

#: Chips, in the order the palette shows them.
TYPES = ("problem", "user", "topic", "contest", "learn", "news")


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


def _matches(source: Source, needle: str) -> QuerySet[Any]:
    queryset, names = _annotated(source)
    rank = Case(
        When(_s=needle, then=Value(0)),
        When(_s__startswith=needle, then=Value(1)),
        When(_s__contains=f" {needle}", then=Value(2)),
        When(_s__contains=needle, then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )
    matched: QuerySet[Any] = (
        queryset.filter(_condition(source, names, needle))
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


def _to_hit(source: Source, row: Any) -> dict[str, Any]:
    return {"type": source.type, "kind": source.kind, **source.hit(row)}


def _group(kind_of: str, needle: str, limit: int, offset: int) -> dict[str, Any]:
    """One type's page: merged across its sources, rank first."""
    found = sources(kind_of)
    count = 0
    rows: list[tuple[int, int, int, Source, Any]] = []
    for index, source in enumerate(found):
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
    return {
        "type": kind_of,
        "count": count,
        "fuzzy": fuzzy,
        "results": [_to_hit(source, row) for _, _, _, source, row in rows[offset : offset + limit]],
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
    return {**empty, "groups": shown, "counts": counts, "total": sum(counts.values())}


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
