"""Find a public problem by what a person types: its slug or its archive number.

Teachers and coaches write `a-plus-b`, `123` or `#123`. One place resolves
that, so a classroom assignment and a coach's recommendation accept the
same spelling and refuse the same problems (unpublished ones).
"""

from __future__ import annotations

from problems.models import Problem


def public_problem(ref: str) -> Problem | None:
    key = ref.strip().lstrip("#")
    if not key:
        return None
    query = (
        Problem.objects.filter(code=int(key)) if key.isdigit() else Problem.objects.filter(slug=key)
    )
    return query.filter(is_public=True).first()


def public_problem_by_id(pk: int) -> Problem | None:
    return Problem.objects.filter(pk=pk, is_public=True).first()


def author_ids(problem: Problem) -> set[int]:
    """The problem's authors (`Problem.authors`), for an "author" mark."""
    return set(problem.authors.values_list("pk", flat=True))


def slugs_by_id(ids: set[int]) -> dict[int, str]:
    """Problem slugs for links in lists that hold only problem ids."""
    if not ids:
        return {}
    return dict(Problem.objects.filter(pk__in=ids).values_list("pk", "slug"))


#: The source-key index is rebuilt at most this often (ADR-0062 § 2.5).
SOURCE_KEYS_CACHE_S = 10 * 60


def source_key_index() -> dict[str, int]:
    """Public problems by the judge-free key of their source URL.

    An article's practice link to, say, Codeforces 1234A attaches to our
    problem imported from that same page (ADR-0062 § 2.5): both sides use
    `content.exercise_keys`. Cached, since every algorithm page reads it.
    """
    from django.core.cache import cache

    from content.exercise_keys import exercise_key

    cached = cache.get("problems:source-keys")
    if cached is not None:
        return dict(cached)
    rows = (
        Problem.objects.filter(is_public=True)
        .exclude(source_url="")
        .values_list("pk", "source_url")
    )
    index = {exercise_key(url): pk for pk, url in rows}
    cache.set("problems:source-keys", index, SOURCE_KEYS_CACHE_S)
    return index


def practice_candidates(
    topic_ids: list[int], difficulty: int, exclude: set[int], limit: int
) -> list[Problem]:
    """Official public problems on these topics, nearest in difficulty first."""
    from django.db.models import F
    from django.db.models.functions import Abs

    if not topic_ids or limit <= 0:
        return []
    return list(
        Problem.objects.filter(is_public=True, is_official=True, topics__in=topic_ids)
        .exclude(pk__in=exclude)
        .distinct()
        .annotate(gap=Abs(F("difficulty") - difficulty))
        .order_by("gap", "code", "pk")[:limit]
    )


def public_problems(ids: list[int]) -> list[Problem]:
    """These problems, public ones only, in the given order."""
    found = {p.pk: p for p in Problem.objects.filter(pk__in=ids, is_public=True)}
    return [found[pk] for pk in ids if pk in found]


def topic_ids(slugs: list[str]) -> list[int]:
    """Ids of the topics that exist among `slugs` (unknown slugs are skipped)."""
    from problems.models import Topic

    return list(Topic.objects.filter(slug__in=slugs).values_list("pk", flat=True))
