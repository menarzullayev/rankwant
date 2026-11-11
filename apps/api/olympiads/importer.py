"""Import the cp.uz olympiad archive from a clone on the host (ADR-0062 § 2.6).

`root` is cp.uz's `content/` directory at a pinned commit (for production:
`git archive <commit> content/seasons content/problems` into a temporary
directory). It holds `seasons/<season>/{season.json,events/,participants/}`
and `problems/<season>/<event>/{event.json,<set>/{set.json,<task>/…}}`.

Safe to run again: rows are updated in place, only published ones come in,
and a row hidden on a removal request (`removed_at`) stays hidden.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from django.db import transaction

from olympiads.models import Event, Participant, ProblemSet, Result, Season, Task

PUBLISHED = "published"
KEP = "KEP.uz"


@dataclass
class Report:
    seasons: int = 0
    events: int = 0
    participants: int = 0
    results: int = 0
    tasks: int = 0
    kept_removed: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


def _json(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _published(doc: dict[str, Any]) -> bool:
    return bool(doc.get("publication_status", PUBLISHED) == PUBLISHED)


def _routes(season: dict[str, Any]) -> list[dict[str, Any]]:
    keep = ("code", "title", "description", "kind", "order")
    return [
        {key: route.get(key) for key in keep}
        for route in season.get("routes") or []
        if route.get("is_visible", True)
    ]


def _resources(event: dict[str, Any]) -> list[dict[str, Any]]:
    keep = ("type", "title", "url", "is_official", "order")
    return [{key: row.get(key) for key in keep} for row in event.get("resources") or []]


def _memberships(event: dict[str, Any]) -> list[dict[str, Any]]:
    keep = ("route_code", "order", "label", "node_style")
    return [{key: row.get(key) for key in keep} for row in event.get("route_memberships") or []]


@transaction.atomic
def import_archive(root: Path, commit: str) -> Report:
    report = Report()
    seasons_dir, problems_dir = root / "seasons", root / "problems"
    for season_dir in sorted(p for p in seasons_dir.iterdir() if (p / "season.json").exists()):
        doc = _json(season_dir / "season.json")
        if not _published(doc):
            continue
        season, _ = Season.objects.update_or_create(
            slug=doc["slug"],
            defaults={
                "title": doc.get("title", ""),
                "summary": doc.get("summary", ""),
                "start_date": _date(doc.get("start_date")),
                "end_date": _date(doc.get("end_date")),
                "routes": _routes(doc),
                "order": int(doc.get("order") or 0),
                "source_commit": commit,
            },
        )
        report.seasons += 1
        _participants(season_dir / "participants", report)
        for path in sorted((season_dir / "events").glob("*.json")):
            _event(season, _json(path), commit, report)
    if problems_dir.exists():
        for event_file in sorted(problems_dir.glob("*/*/event.json")):
            _tasks(event_file, report)
    return report


def _participants(folder: Path, report: Report) -> None:
    for path in sorted(folder.glob("*.json")):
        doc = _json(path)
        existing = Participant.objects.filter(slug=doc["slug"]).first()
        if existing is not None and existing.removed_at is not None:
            report.kept_removed.append(f"participant:{doc['slug']}")
            continue
        Participant.objects.update_or_create(
            slug=doc["slug"],
            defaults={
                "full_name": doc.get("full_name", ""),
                "country_code": doc.get("country_code", ""),
            },
        )
        report.participants += 1


def _event(season: Season, doc: dict[str, Any], commit: str, report: Report) -> None:
    if not _published(doc):
        return
    event, _ = Event.objects.update_or_create(
        slug=doc["slug"],
        defaults={
            "season": season,
            "code": doc.get("code", ""),
            "title": doc.get("title", ""),
            "short_title": doc.get("short_title", ""),
            "summary": doc.get("summary", ""),
            "description": doc.get("description", ""),
            "kind": doc.get("type", ""),
            "status": doc.get("event_status", ""),
            "verification": doc.get("verification_status", ""),
            "start_date": _date(doc.get("start_date")),
            "end_date": _date(doc.get("end_date")),
            "date_label": doc.get("date_label", ""),
            "location": doc.get("location", ""),
            "mode": doc.get("mode", ""),
            "platform": doc.get("platform", ""),
            "organizer": doc.get("organizer", ""),
            "eligibility": doc.get("eligibility", ""),
            "is_featured": bool(doc.get("is_featured")),
            "order": int(doc.get("order") or 0),
            "routes": _memberships(doc),
            "resources": _resources(doc),
            "source_commit": commit,
        },
    )
    report.events += 1
    kept: set[int] = set()
    for row in doc.get("results") or []:
        participant = Participant.objects.filter(slug=row.get("participant")).first()
        if participant is None:
            report.missing.append(f"{event.slug}: participant {row.get('participant')}")
            continue
        if participant.removed_at is not None:
            continue
        result, _ = Result.objects.update_or_create(
            event=event,
            participant=participant,
            defaults={
                "rank": row.get("rank"),
                "score": row.get("score"),
                "medal": row.get("medal") or "",
                "is_local": bool(row.get("is_local", True)),
                "result_url": row.get("result_url") or "",
                "order": int(row.get("order") or 0),
            },
        )
        kept.add(result.pk)
        report.results += 1
    # A result the source no longer lists goes (a corrected scoreboard).
    event.results.exclude(pk__in=kept).delete()


def _tasks(event_file: Path, report: Report) -> None:
    doc = _json(event_file)
    event = Event.objects.filter(slug=doc.get("event_slug")).first()
    if event is None:
        report.missing.append(f"event {doc.get('event_slug')} for statements")
        return
    for order, set_slug in enumerate(doc.get("sets") or [], start=1):
        set_dir = event_file.parent / set_slug
        set_doc = _json(set_dir / "set.json")
        if not _published(set_doc):
            continue
        problem_set, _ = ProblemSet.objects.update_or_create(
            event=event,
            slug=set_doc.get("slug", set_slug),
            defaults={
                "title": set_doc.get("title", set_slug),
                "description": set_doc.get("description", ""),
                "order": int(set_doc.get("order") or order),
            },
        )
        for task_order, task_slug in enumerate(set_doc.get("problems") or [], start=1):
            _task(problem_set, set_dir / task_slug, task_order, report)


def _task(problem_set: ProblemSet, folder: Path, order: int, report: Report) -> None:
    doc = _json(folder / "problem.json")
    if not _published(doc):
        return
    existing = Task.objects.filter(problem_set=problem_set, slug=doc["slug"]).first()
    if existing is not None and existing.removed_at is not None:
        report.kept_removed.append(f"task:{problem_set.event_id}/{doc['slug']}")
        return
    statement_file = folder / doc.get("statement_file", "statement.uz.md")
    links = [
        {key: row.get(key) for key in ("kind", "title", "url", "platform", "is_official")}
        for row in doc.get("links") or []
    ]
    Task.objects.update_or_create(
        problem_set=problem_set,
        slug=doc["slug"],
        defaults={
            "code": doc.get("code", ""),
            "title": doc.get("title", ""),
            "original_title": doc.get("original_title", ""),
            "statement": statement_file.read_text(encoding="utf-8")
            if statement_file.exists()
            else "",
            "translation_status": doc.get("translation_status", ""),
            "problem_type": doc.get("problem_type", ""),
            "time_limit_ms": doc.get("time_limit_ms"),
            "memory_limit_mb": doc.get("memory_limit_mb"),
            "max_score": doc.get("max_score"),
            "tags": list(doc.get("tags") or []),
            "links": links,
            "statement_pdf": (doc.get("statement_pdf") or {}).get("url", "") or "",
            "order": int(doc.get("order") or order),
            "from_kep": any(
                row.get("platform") == KEP and row.get("kind") == "original" for row in links
            ),
        },
    )
    report.tasks += 1
