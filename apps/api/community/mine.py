"""My content (decision 2026-11-11 ④): reports about what a person wrote.

Problems, blog entries and comments in one list, newest first. The reporter
is never named: the author fixes the content, not the person.
"""

from __future__ import annotations

from typing import Any

from community.models import Comment, Entry, Kind, Report, Target

LIMIT = 200


def _comment_links(rows: list[Comment]) -> dict[int, str]:
    from problems.lookup import slugs_by_id

    slugs = slugs_by_id({r.target_id for r in rows if r.target_type == Target.PROBLEM})
    links: dict[int, str] = {}
    for row in rows:
        if row.target_type == Target.PROBLEM and row.target_id in slugs:
            links[row.pk] = f"/problems/{slugs[row.target_id]}?tab=discussion#c{row.pk}"
        elif row.target_type == Target.ENTRY:
            links[row.pk] = f"/blogs/{row.target_id}#c{row.pk}"
    return links


def reports_about(user_id: int) -> list[dict[str, Any]]:
    from problems.reports import for_author

    entries = {e.pk: e for e in Entry.objects.filter(author_id=user_id)}
    comments = {c.pk: c for c in Comment.objects.filter(author_id=user_id)}
    links = _comment_links(list(comments.values()))
    out: list[dict[str, Any]] = list(for_author(user_id, LIMIT))
    rows = (
        Report.objects.filter(kind=Kind.ENTRY, object_id__in=list(entries))
        | Report.objects.filter(kind=Kind.COMMENT, object_id__in=list(comments))
    ).order_by("-created_at")[:LIMIT]
    for row in rows:
        if row.kind == Kind.ENTRY:
            entry = entries[row.object_id]
            title, link = entry.title, f"/blogs/{entry.pk}"
        else:
            comment = comments[row.object_id]
            title, link = comment.body[:80], links.get(comment.pk, "")
        out.append(
            {
                "kind": row.kind,
                "title": title,
                "link": link,
                "reason": row.reason,
                "note": row.note,
                "status": row.status,
                "created_at": row.created_at,
            }
        )
    out.sort(key=lambda item: item["created_at"], reverse=True)
    return out[:LIMIT]
