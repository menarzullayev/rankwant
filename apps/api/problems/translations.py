"""A problem's statement in the reader's language (ADR-0058).

The author's language lives on `Problem`; every other language is a
`ProblemTranslation` row. A reader gets the row for their language when one
exists, field by field: an empty translated field falls back to the
problem's own text, so a partial translation never blanks a block.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from django.conf import settings
from django.db.models import Prefetch
from django.utils.translation import get_language
from rest_framework.request import Request

from core.search import normalize_search
from problems.models import Problem, ProblemTranslation

LOCALES: frozenset[str] = frozenset(code for code, _ in settings.LANGUAGES)
#: Text fields that have a translation.
FIELDS = ("title", "statement", "input_format", "output_format", "note", "editorial")
#: Where the list keeps the reader's one translation (see `prefetch`).
READER_ROWS = "reader_translations"


def reader_locale(request: Request | None) -> str:
    """`?lang=` when it is a site language, else the request's language."""
    raw = ""
    if request is not None:
        raw = str(request.query_params.get("lang") or "")
    for candidate in (raw, get_language() or "", getattr(request, "LANGUAGE_CODE", "") or ""):
        code = candidate.split("-")[0].lower()
        if code in LOCALES:
            return code
    return settings.LANGUAGE_CODE


def prefetch(locale: str, through: str = "translations") -> Prefetch[Any]:
    """Only the reader's translation, for a list of problems (or a relation
    that ends in their translations)."""
    return Prefetch(
        through,
        queryset=ProblemTranslation.objects.filter(locale=locale),
        to_attr=READER_ROWS,
    )


def _row(problem: Problem, locale: str, rows: Iterable[ProblemTranslation] | None) -> Any:
    if locale == problem.statement_locale:
        return None
    if rows is None:
        rows = getattr(problem, READER_ROWS, None)
    if rows is None:
        rows = problem.translations.all()
    return next((row for row in rows if row.locale == locale), None)


def apply(data: dict[str, Any], problem: Problem, locale: str, rows: Any = None) -> str:
    """Put the reader's language into a serialized problem; return the language shown.

    Only fields already in `data` are touched, and the editorial only when
    the reader may see it (a locked editorial is serialized as "").
    """
    row = _row(problem, locale, rows)
    if row is None:
        return problem.statement_locale
    for field in FIELDS:
        if field not in data:
            continue
        if field == "editorial" and not data[field]:
            continue
        value = getattr(row, field)
        if value:
            data[field] = value
    shown_locale: str = row.locale
    return shown_locale


def title(problem: Problem, locale: str) -> str:
    """The problem's title in the reader's language, else the author's."""
    row = _row(problem, locale, None)
    return str(row.title) if row is not None and row.title else problem.title


def shown(problem: Problem, locale: str) -> str:
    """The language `apply` shows for this reader."""
    row = _row(problem, locale, None)
    return row.locale if row is not None else problem.statement_locale


def available(problem: Problem) -> list[str]:
    """The author's language first, then the translations."""
    others = sorted(problem.translations.values_list("locale", flat=True))
    return [
        problem.statement_locale,
        *[code for code in others if code != problem.statement_locale],
    ]


def refresh_titles(problem_id: int) -> None:
    """Keep `Problem.translated_titles` in step for the site search."""
    titles = ProblemTranslation.objects.filter(problem_id=problem_id).values_list(
        "title", flat=True
    )
    text = "\n".join(normalize_search(title) for title in titles if title)
    Problem.objects.filter(pk=problem_id).update(translated_titles=text)


def on_change(sender: Any, instance: ProblemTranslation, **kwargs: Any) -> None:
    refresh_titles(instance.problem_id)
