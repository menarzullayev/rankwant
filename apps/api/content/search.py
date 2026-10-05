"""Articles, algorithms and learning paths in the site search (see `core.search`)."""

from content.models import Article, Roadmap
from core.search import Source, register

for _kind in (Article.Kind.ARTICLE, Article.Kind.ALGORITHM):
    register(
        Source(
            type="learn",
            kind=str(_kind),
            queryset=lambda kind=_kind: Article.objects.filter(is_published=True, kind=kind),  # type: ignore[misc]
            primary="title",
            secondary=("summary", "body"),
            excerpt=("body",),
            order=("difficulty", "pk"),
            hit=lambda article: {
                "key": article.slug,
                "title": article.title,
                "subtitle": article.summary,
                "meta": article.reading_minutes,
            },
        )
    )

register(
    Source(
        type="learn",
        kind="roadmap",
        queryset=lambda: Roadmap.objects.filter(is_published=True),
        primary="title",
        secondary=("description",),
        excerpt=("description",),
        order=("order", "pk"),
        hit=lambda roadmap: {"key": roadmap.slug, "title": roadmap.title},
    )
)
