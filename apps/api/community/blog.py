"""Member blogs (decision 2026-11-11 ④⑥⑦⑧).

Anyone may write; post-moderation hides what three people report; a new
account writes one entry a day; a link needs a confirmed e-mail; the
author's followers hear about a new entry.
"""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Any

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, IntegerField, OuterRef, QuerySet, Subquery, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from community.models import Comment, Entry, Target
from community.services import NEW_ACCOUNT, CommunityError, Place, is_moderator
from core.models import User

TITLE_MIN = 3
TITLE_MAX = 200
BODY_MIN = 10
BODY_MAX = 20000
MAX_TAGS = 5
TAG_MAX = 24
#: A new account: one entry a day (owner decision ⑥); everyone: a flood guard.
NEW_DAILY_ENTRIES = 1
DAILY_ENTRIES = 10
#: "Popular" looks at this window.
TOP_WINDOW = timedelta(days=7)
#: A view from the same reader counts once in this window.
VIEW_WINDOW = 60 * 60

TAG = re.compile(r"^[\w-]+$")
LINK = re.compile(r"(https?://|www\.)", re.IGNORECASE)
TABS = ("new", "top", "following")


def clean_tags(raw: list[str] | str) -> str:
    """`,a,b,` from what the author typed: lower case, spaces as dashes."""
    items = raw.split(",") if isinstance(raw, str) else raw
    tags: list[str] = []
    for item in items:
        tag = re.sub(r"\s+", "-", str(item).strip().lower().lstrip("#"))
        if not tag:
            continue
        if len(tag) > TAG_MAX or not TAG.match(tag):
            raise CommunityError(
                f"A tag is letters, digits and dashes, at most {TAG_MAX}", error="entry_tag"
            )
        if tag not in tags:
            tags.append(tag)
    if len(tags) > MAX_TAGS:
        raise CommunityError(f"At most {MAX_TAGS} tags", error="entry_tags_many")
    return f",{','.join(tags)}," if tags else ""


def _clean(user: User, title: str, body: str) -> tuple[str, str]:
    title, body = (title or "").strip(), (body or "").strip()
    if not TITLE_MIN <= len(title) <= TITLE_MAX:
        raise CommunityError(f"A title is {TITLE_MIN}–{TITLE_MAX} characters", error="entry_title")
    if not BODY_MIN <= len(body) <= BODY_MAX:
        raise CommunityError(f"The text is {BODY_MIN}–{BODY_MAX} characters", error="entry_body")
    if (LINK.search(body) or LINK.search(title)) and not user.email_verified:
        raise CommunityError("Confirm your e-mail to post links", error="comment_link_unverified")
    return title, body


def _check_pace(user: User) -> None:
    since = timezone.now() - timedelta(days=1)
    written = Entry.objects.filter(author=user, created_at__gte=since).count()
    new = user.date_joined is not None and timezone.now() - user.date_joined < NEW_ACCOUNT
    cap = NEW_DAILY_ENTRIES if new else DAILY_ENTRIES
    if written >= cap:
        raise CommunityError(f"At most {cap} entries a day", error="entry_daily_limit")


def _tell_followers(entry: Entry, author: User) -> int:
    """⑧: the author's followers hear about the new entry."""
    from notifications.services import notify_many
    from profiles.follows import follower_ids

    ids = follower_ids(author.pk)
    if not ids:
        return 0
    return notify_many(
        User.objects.filter(pk__in=ids, is_active=True),
        "system",
        code="blog_entry",
        params={"user": author.username, "title": entry.title, "entry": str(entry.pk)},
        ref_type="entry",
        ref_id=entry.pk,
    )


@transaction.atomic
def create(user: User, title: str, body: str, tags: list[str] | str) -> Entry:
    title, body = _clean(user, title, body)
    tag_text = clean_tags(tags)
    _check_pace(user)
    entry = Entry.objects.create(author=user, title=title, body=body, tags=tag_text)
    transaction.on_commit(lambda: _tell_followers(entry, user))
    return entry


def _own(user: User, entry_id: int) -> Entry:
    entry = Entry.objects.select_for_update().filter(pk=entry_id).first()
    if entry is None or entry.is_deleted:
        raise CommunityError("Entry not found", error="entry_not_found")
    if entry.author_id != user.pk:
        raise CommunityError("Not your entry", error="entry_not_yours")
    if entry.is_hidden:
        raise CommunityError("The entry was hidden", error="entry_hidden")
    return entry


@transaction.atomic
def edit(user: User, entry_id: int, title: str, body: str, tags: list[str] | str) -> Entry:
    entry = _own(user, entry_id)
    entry.title, entry.body = _clean(user, title, body)
    entry.tags = clean_tags(tags)
    entry.edited_at = timezone.now()
    entry.save(update_fields=["title", "body", "tags", "edited_at", "updated_at"])
    return entry


@transaction.atomic
def remove(user: User, entry_id: int) -> Entry:
    entry = _own(user, entry_id)
    entry.is_deleted = True
    entry.save(update_fields=["is_deleted", "updated_at"])
    return entry


def readable(viewer: Any) -> QuerySet[Entry]:
    """Entries a reader may open: not deleted; hidden ones only for staff."""
    rows = Entry.objects.filter(is_deleted=False)
    return rows if is_moderator(viewer) else rows.filter(is_hidden=False)


def with_comment_count(rows: QuerySet[Entry]) -> QuerySet[Entry]:
    visible = (
        Comment.objects.filter(
            target_type=Target.ENTRY, target_id=OuterRef("pk"), is_hidden=False, is_deleted=False
        )
        .order_by()
        .values("target_id")
        .annotate(n=Count("pk"))
        .values("n")[:1]
    )
    return rows.annotate(
        comment_count=Coalesce(Subquery(visible, output_field=IntegerField()), Value(0))
    )


def feed(viewer: Any, tab: str = "new", tag: str = "", author: str = "") -> QuerySet[Entry]:
    rows = Entry.objects.filter(is_deleted=False, is_hidden=False).select_related("author")
    if tag:
        rows = rows.filter(tags__contains=f",{tag.strip().lower()},")
    if author:
        rows = rows.filter(author__username=author)
    if tab == "top":
        rows = rows.filter(created_at__gte=timezone.now() - TOP_WINDOW, score__gt=0).order_by(
            "-score", "-created_at"
        )
    elif tab == "following":
        if not getattr(viewer, "is_authenticated", False):
            return rows.none()
        from profiles.follows import following_ids

        rows = rows.filter(author_id__in=following_ids(viewer.pk)).order_by("-created_at")
    else:
        rows = rows.order_by("-created_at", "-pk")
    return with_comment_count(rows)


def count_view(entry: Entry, viewer: Any, address: str) -> None:
    """One view per reader an hour; the author's own visits do not count."""
    signed_in = getattr(viewer, "is_authenticated", False)
    if signed_in and viewer.pk == entry.author_id:
        return
    who = f"u{viewer.pk}" if signed_in else f"a{address}"
    if cache.add(f"entry-view:{entry.pk}:{who}", 1, VIEW_WINDOW):
        from django.db.models import F

        Entry.objects.filter(pk=entry.pk).update(view_count=F("view_count") + 1)


def entry_place(ref: str) -> Place | None:
    """The discussion under a readable entry."""
    if not ref.isdigit():
        return None
    entry = Entry.objects.filter(pk=int(ref), is_deleted=False, is_hidden=False).first()
    if entry is None:
        return None
    return Place(
        type=Target.ENTRY,
        id=entry.pk,
        title=entry.title,
        link={"entry": str(entry.pk)},
        owners=frozenset({entry.author_id} if entry.author_id else set()),
        problem_id=None,
    )


def popular_tags(limit: int = 20) -> list[tuple[str, int]]:
    """Tags of the last 90 days, most used first."""
    counts: dict[str, int] = {}
    since = timezone.now() - timedelta(days=90)
    for text in Entry.objects.filter(
        is_deleted=False, is_hidden=False, created_at__gte=since
    ).values_list("tags", flat=True)[:2000]:
        for tag in text.split(","):
            if tag:
                counts[tag] = counts.get(tag, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
