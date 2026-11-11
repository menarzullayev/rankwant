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
