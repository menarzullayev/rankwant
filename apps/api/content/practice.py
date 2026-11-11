"""Practice "on this site" for an algorithm article (ADR-0062 § 2.5).

Three layers, in this order, without repeats:

1. **Editor picks** — `ArticleProblemLink` rows with the practice role.
2. **Same source** — our problem imported from the very page an external
   practice link points to (matched by `content.exercise_keys`).
3. **Topic and difficulty** — official public problems on the article's
   topics, nearest to its difficulty, to fill the list.

The external links themselves are shown apart ("on other sites").
"""

from __future__ import annotations

from typing import Any

from content.models import Article, ArticleProblemLink
from problems.lookup import practice_candidates, public_problems, source_key_index

#: How many problems the "on this site" list shows; editor picks are never cut.
PRACTICE_HERE = 8


def practice_here(article: Article) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[int] = set()

    def add(problem: Any, via: str) -> None:
        if problem.pk in seen:
            return
        seen.add(problem.pk)
        rows.append(
            {
                "slug": problem.slug,
                "title": problem.title,
                "code": problem.code,
                "difficulty": problem.difficulty,
                "via": via,
            }
        )

    for link in article.problem_links.all():
        if link.role == ArticleProblemLink.Role.PRACTICE and link.problem.is_public:
            add(link.problem, "pick")
    index = source_key_index()
    matched = [index[link.key] for link in article.external_links.all() if link.key in index]
    for problem in public_problems(matched):
        add(problem, "source")
    room = max(PRACTICE_HERE - len(rows), 0)
    topics = [topic.pk for topic in article.topics.all()]
    for problem in practice_candidates(topics, article.difficulty, seen, room):
        add(problem, "topic")
    return rows
