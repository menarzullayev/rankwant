"""Community rules: who may write, what a reader sees, votes and reports.

Owner decisions of 2026-11-11 (`docs/decisions/2026-11-11-community-details.md`):

① replies form a tree; ② a code block is hidden from a reader who has not
solved the problem; ⑤ everyone may vote ±1; ⑥ post-moderation — a comment
appears at once and three reports from different people hide it; a new
account writes at most 5 comments a day, and a link needs a confirmed
e-mail; ⑧ a reply and an @mention notify.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.db.models import F, Model
from django.utils import timezone

from community.models import Comment, Entry, Kind, Report, Target, Vote
from core.models import User
from core.permissions import STAFF_GROUP_CONTENT, has_staff_group

log = logging.getLogger(__name__)

BODY_MIN = 2
BODY_MAX = 2000
#: Deeper replies are still stored; the page stops indenting at 4.
MAX_DEPTH = 32
#: An account younger than this is "new" (owner decision ⑥).
NEW_ACCOUNT = timedelta(days=7)
NEW_DAILY_COMMENTS = 5
#: Everyone: a flood guard, not a quota.
DAILY_COMMENTS = 100
#: Reports from this many different people hide a comment at once.
AUTO_HIDE_REPORTS = 3
MAX_MENTIONS = 5

LINK = re.compile(r"(https?://|www\.)", re.IGNORECASE)
MENTION = re.compile(r"(?<![\w@])@([A-Za-z0-9_][A-Za-z0-9_.-]{2,31})")
#: A fenced code block, ``` or ~~~, closed or running to the end.
FENCE = re.compile(r"^([ \t]{0,3})(`{3,}|~{3,})[^\n]*\n.*?(?:^[ \t]{0,3}\2[ \t]*$|\Z)", re.M | re.S)
#: What a reader who may not see the code gets in its place; the site
#: draws a "solve it first" box there.
HIDDEN_CODE = "[[hidden-code]]"
#: Indented code (4 spaces or a tab) after a blank line or at the start.
INDENTED = re.compile(r"(\A|\n[ \t]*\n)((?:(?: {4}|\t)[^\n]*\S[^\n]*(?:\n|\Z))+)")
#: An inline span: one line of code. Short ones (a variable, `n`) stay.
INLINE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
INLINE_HIDDEN_FROM = 40


class CommunityError(Exception):
    def __init__(self, message: str, error: str) -> None:
        super().__init__(message)
        #: The API error code (`error.<code>` on the site), not a notification code.
        self.code = error


@dataclass(frozen=True)
class Place:
    """Where a thread lives: a public problem now, a blog entry later."""

    type: str
    id: int
    title: str
    #: Parameters the site turns into a link (`notificationHref`).
    link: dict[str, str]
    #: People shown with the "author" mark: the problem's authors.
    owners: frozenset[int] = field(default_factory=frozenset)
    #: Code is hidden from readers who have not solved this problem (②).
    problem_id: int | None = None


def problem_place(ref: str) -> Place | None:
    """A public problem's discussion. A problem still inside a running
    contest is not public (ADR-0055), so its discussion stays closed."""
    from problems.lookup import author_ids, public_problem

    problem = public_problem(ref)
    if problem is None:
        return None
    return Place(
        type=Target.PROBLEM,
        id=problem.pk,
        title=problem.title,
        link={"problem": problem.slug},
        owners=frozenset(author_ids(problem)),
        problem_id=problem.pk,
    )


def place_of(comment: Comment) -> Place | None:
    if comment.target_type == Target.PROBLEM:
        from problems.lookup import public_problem_by_id

        problem = public_problem_by_id(comment.target_id)
        return problem_place(problem.slug) if problem is not None else None
    if comment.target_type == Target.ENTRY:
        from community.blog import entry_place

        return entry_place(str(comment.target_id))
    return None


def is_moderator(user: Any) -> bool:
    return bool(getattr(user, "is_authenticated", False)) and (
        user.is_superuser or has_staff_group(user, STAFF_GROUP_CONTENT)
    )


def may_see_code(viewer: Any, place: Place) -> bool:
    """②: code is open to whoever solved the problem, its authors and staff."""
    if place.problem_id is None:
        return True
    if not getattr(viewer, "is_authenticated", False):
        return False
    if viewer.pk in place.owners or is_moderator(viewer):
        return True
    from ratings.solved import solved_ids

    return bool(solved_ids(viewer.pk, [place.problem_id]))


def hide_code(body: str) -> tuple[str, int]:
    """The body with its code replaced by a marker: fenced and indented
    blocks, and inline spans long enough to hold a one-line solution."""
    count = 0

    def swap(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return HIDDEN_CODE

    def swap_indented(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return match.group(1) + HIDDEN_CODE + "\n"

    def swap_inline(match: re.Match[str]) -> str:
        nonlocal count
        if len(match.group(2).strip()) < INLINE_HIDDEN_FROM:
            return match.group(0)
        count += 1
        return HIDDEN_CODE

    text = FENCE.sub(swap, body)
    text = INDENTED.sub(swap_indented, text)
    text = INLINE.sub(swap_inline, text)
    return text, count


def _clean(body: str) -> str:
    text = (body or "").strip()
    if len(text) < BODY_MIN:
        raise CommunityError("The comment is too short", error="comment_short")
    if len(text) > BODY_MAX:
        raise CommunityError(f"At most {BODY_MAX} characters", error="comment_long")
    return text


def _check_links(user: User, text: str) -> None:
    if LINK.search(text) and not user.email_verified:
        raise CommunityError("Confirm your e-mail to post links", error="comment_link_unverified")


def _check_pace(user: User) -> None:
    since = timezone.now() - timedelta(days=1)
    written = Comment.objects.filter(author=user, created_at__gte=since).count()
    new = user.date_joined is not None and timezone.now() - user.date_joined < NEW_ACCOUNT
    cap = NEW_DAILY_COMMENTS if new else DAILY_COMMENTS
    if written >= cap:
        raise CommunityError(f"At most {cap} comments a day", error="comment_daily_limit")


def _notify(to: User, code: str, comment: Comment, place: Place, author: User) -> None:
    from notifications.services import notify

    notify(
        to,
        "system",
        code=code,
        params={
            "user": author.username,
            "title": place.title,
            "comment": str(comment.pk),
            **place.link,
        },
        ref_type="comment",
        ref_id=comment.pk,
    )


def _mentioned(text: str, author: User, skip: set[int]) -> list[User]:
    plain, _ = hide_code(text)
    names: list[str] = []
    for name in MENTION.findall(plain):
        if name.lower() not in (n.lower() for n in names):
            names.append(name)
        if len(names) >= MAX_MENTIONS:
            break
    if not names:
        return []
    # Exact names: a case-insensitive pattern would scan every user row.
    found = User.objects.filter(username__in=names)
    return [u for u in found.filter(is_active=True) if u.pk != author.pk and u.pk not in skip]


@transaction.atomic
def post(user: User, place: Place, body: str, parent_id: int | None = None) -> Comment:
    text = _clean(body)
    _check_links(user, text)
    _check_pace(user)
    parent = None
    if parent_id is not None:
        parent = (
            Comment.objects.select_related("author")
            .filter(pk=parent_id, target_type=place.type, target_id=place.id)
            .first()
        )
        if parent is None:
            raise CommunityError("The comment you reply to is gone", error="comment_not_found")
        if parent.is_hidden or parent.is_deleted:
            raise CommunityError("You cannot reply to a removed comment", error="comment_removed")
    comment = Comment.objects.create(
        target_type=place.type,
        target_id=place.id,
        author=user,
        parent=parent,
        root=(parent.root or parent) if parent is not None else None,
        depth=min(parent.depth + 1, MAX_DEPTH) if parent is not None else 0,
        body=text,
    )
    notified: set[int] = set()
    if parent is not None and parent.author is not None and parent.author_id != user.pk:
        _notify(parent.author, "comment_reply", comment, place, user)
        notified.add(parent.author.pk)
    for person in _mentioned(text, user, notified):
        _notify(person, "comment_mention", comment, place, user)
    return comment


def _own(user: User, comment_id: int) -> Comment:
    comment = Comment.objects.select_for_update().filter(pk=comment_id).first()
    if comment is None:
        raise CommunityError("Comment not found", error="comment_not_found")
    if comment.author_id != user.pk:
        raise CommunityError("Not your comment", error="comment_not_yours")
    if comment.is_deleted or comment.is_hidden:
        raise CommunityError("The comment was removed", error="comment_removed")
    return comment


@transaction.atomic
def edit(user: User, comment_id: int, body: str) -> Comment:
    comment = _own(user, comment_id)
    text = _clean(body)
    _check_links(user, text)
    comment.body = text
    comment.edited_at = timezone.now()
    comment.save(update_fields=["body", "edited_at", "updated_at"])
    return comment


@transaction.atomic
def remove(user: User, comment_id: int) -> Comment:
    """The author deletes: the text goes, the place in the thread stays."""
    comment = _own(user, comment_id)
    comment.is_deleted = True
    comment.save(update_fields=["is_deleted", "updated_at"])
    return comment


# --- votes -------------------------------------------------------------------

#: What can be voted on and reported: kind → model.
VOTABLE: dict[str, type[Model]] = {Kind.COMMENT: Comment, Kind.ENTRY: Entry}


def _votable(kind: str, object_id: int) -> Any:
    model = VOTABLE.get(kind)
    if model is None:
        raise CommunityError("Unknown kind", error="vote_kind")
    row = model._default_manager.select_for_update().filter(pk=object_id).first()  # type: ignore[attr-defined]
    if row is None:
        raise CommunityError("Not found", error="comment_not_found")
    return row


@transaction.atomic
def vote(user: User, kind: str, object_id: int, value: int) -> tuple[int, int]:
    """±1 or 0 (take the vote back). Returns the new score and the reader's vote."""
    if value not in (-1, 0, 1):
        raise CommunityError("A vote is -1, 0 or 1", error="vote_value")
    row = _votable(kind, object_id)
    if row.author_id == user.pk:
        raise CommunityError("You cannot vote for yourself", error="vote_self")
    if row.is_deleted or row.is_hidden:
        raise CommunityError("The comment was removed", error="comment_removed")
    mine = Vote.objects.filter(user=user, kind=kind, object_id=object_id).first()
    before = mine.value if mine is not None else 0
    if value == before:
        return int(row.score), value
    if value == 0:
        assert mine is not None
        mine.delete()
    elif mine is None:
        Vote.objects.create(
            user=user, kind=kind, object_id=object_id, value=value, author_id=row.author_id
        )
    else:
        mine.value = value
        mine.save(update_fields=["value"])
    type(row)._default_manager.filter(pk=row.pk).update(score=F("score") + (value - before))
    row.refresh_from_db(fields=["score"])
    return int(row.score), value


# --- reports and moderation ---------------------------------------------------


@transaction.atomic
def report(user: User, kind: str, object_id: int, reason: str, note: str = "") -> Report:
    if reason not in Report.Reason.values:
        raise CommunityError("Unknown reason", error="report_reason")
    row = _votable(kind, object_id)
    if row.author_id == user.pk:
        raise CommunityError("You cannot report yourself", error="report_self")
    if Report.objects.filter(reporter=user, kind=kind, object_id=object_id).exists():
        raise CommunityError("Already reported", error="report_already")
    made = Report.objects.create(
        reporter=user, kind=kind, object_id=object_id, reason=reason, note=note[:300]
    )
    reporters = Report.objects.filter(kind=kind, object_id=object_id).count()
    fields = {"report_count": reporters}
    if reporters >= AUTO_HIDE_REPORTS and not row.is_hidden:
        # ⑥: three different people — hidden now, staff decides later.
        fields["is_hidden"] = True
    type(row)._default_manager.filter(pk=row.pk).update(**fields)
    return made


@transaction.atomic
def moderate(staff: User, kind: str, object_id: int, *, hide: bool) -> Any:
    """Staff hides (reports accepted) or restores (reports rejected)."""
    row = _votable(kind, object_id)
    row.is_hidden = hide
    row.save(update_fields=["is_hidden", "updated_at"])
    Report.objects.filter(kind=kind, object_id=object_id, status=Report.Status.OPEN).update(
        status=Report.Status.ACCEPTED if hide else Report.Status.REJECTED,
        handled_by=staff,
        handled_at=timezone.now(),
    )
    return row


# --- reading ------------------------------------------------------------------

THREADS_PER_PAGE = 20


def thread_page(place: Place, viewer: Any, before: int | None = None) -> dict[str, Any]:
    """A page of threads, newest first, with every reply under them.

    Replies inside a thread go oldest first, as a conversation reads.
    """
    base = Comment.objects.filter(target_type=place.type, target_id=place.id)
    roots_q = base.filter(root__isnull=True).order_by("-pk")
    if before is not None:
        roots_q = roots_q.filter(pk__lt=before)
    roots = list(roots_q.select_related("author")[: THREADS_PER_PAGE + 1])
    more = len(roots) > THREADS_PER_PAGE
    roots = roots[:THREADS_PER_PAGE]
    replies = list(
        base.filter(root__in=roots).select_related("author").order_by("created_at", "pk")
    )
    rows = roots + replies
    ids = [row.pk for row in rows]
    signed_in = bool(getattr(viewer, "is_authenticated", False))
    votes: dict[int, int] = {}
    if signed_in and ids:
        votes = dict(
            Vote.objects.filter(user=viewer, kind=Kind.COMMENT, object_id__in=ids).values_list(
                "object_id", "value"
            )
        )
    solvers: set[int] = set()
    if place.problem_id is not None:
        from ratings.solved import solvers_among

        solvers = solvers_among(place.problem_id, {r.author_id for r in rows if r.author_id})
    return {
        "count": base.filter(is_hidden=False, is_deleted=False).count(),
        "next": roots[-1].pk if more and roots else None,
        "code_open": may_see_code(viewer, place),
        "rows": rows,
        "votes": votes,
        "solvers": solvers,
        "moderator": is_moderator(viewer),
        "viewer_id": viewer.pk if signed_in else None,
        "place": place,
    }


def visible(
    row: Comment, *, code_open: bool, moderator: bool, viewer_id: int | None
) -> dict[str, Any]:
    """What one reader may see of one comment."""
    removed = row.is_deleted or row.is_hidden
    body, hidden_code = row.body, 0
    if removed and not moderator:
        body = ""
    elif not code_open and row.author_id != viewer_id:
        body, hidden_code = hide_code(body)
    return {
        "body": body,
        "hidden_code": hidden_code,
        "author": None if row.is_deleted and not moderator else row.author,
    }
