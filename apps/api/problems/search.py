"""Problems and topics in the site search (see `core.search`)."""

from django.db.models import Q

from core.search import Source, register
from problems.models import Problem, Topic


def by_number(needle: str) -> Q | None:
    """`1519` or `#1519` — the number a problem is printed with."""
    digits = needle.removeprefix("#").strip()
    if not digits.isdigit() or len(digits) > 9:
        return None
    return Q(code=int(digits))


register(
    Source(
        type="problem",
        kind="problem",
        queryset=lambda: Problem.objects.filter(is_public=True),
        primary="title_search",
        stored=True,
        secondary=("slug",),
        exact=by_number,
        order=("difficulty", "pk"),
        hit=lambda problem: {
            "key": problem.slug,
            "title": problem.title,
            "code": problem.code,
            "meta": problem.difficulty,
        },
    )
)

register(
    Source(
        type="topic",
        kind="topic",
        queryset=Topic.objects.all,
        primary="name_search",
        stored=True,
        secondary=("slug", "name_ru", "name_en"),
        order=("slug",),
        hit=lambda topic: {
            "key": topic.slug,
            "title": topic.name_uz,
            "title_ru": topic.name_ru,
            "title_en": topic.name_en,
        },
    )
)
