"""Posts in the site search (see `core.search`)."""

from blog.models import Post
from core.search import Source, register

register(
    Source(
        type="news",
        kind="post",
        queryset=lambda: Post.objects.filter(is_published=True),
        primary="title",
        secondary=("summary", "body"),
        excerpt=("body",),
        order=("-published_at", "pk"),
        hit=lambda post: {
            "key": post.slug,
            "title": post.title,
            "subtitle": post.summary,
            "date": post.published_at,
        },
    )
)
