"""Import the vendored cp.uz algorithms library (ADR-0062).

The snapshot lives next to this module (`content/cpuz/`), built by
`tools/cpuz_snapshot.py` from cp.uz and cp-algorithms at pinned commits, and
reviewed in pull requests. This module loads it into the database:

- one `Article` per entry, `kind=algorithm`, the Uzbek text as its body;
- the English original as its `en` `ArticleTranslation`;
- the practice links as `ArticleExternalLink`, with their judge-free key;
- the review log from `reviews/<id>.json`, one file per article (written by
  the agent review, so reviewers working in parallel never touch one file).

Running it again changes only what changed. An article whose body was edited
here since it was imported keeps the edit (§ 2.1), and nothing is published
unless asked: the whole library goes out together (§ 2.3), and an article
still waiting for its review never does.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from content.cpuz_topics import topics_for
from content.models import Article, ArticleExternalLink, ArticleReview, ArticleTranslation
from problems.lookup import topic_ids

SNAPSHOT = Path(__file__).resolve().parent / "cpuz"
IMPORT_ACTOR = "cpuz-import"
#: The library's three levels on our 800–3500 difficulty scale, so the
#: imported articles sort among our own ones.
LEVEL_DIFFICULTY = {"beginner": 1000, "intermediate": 1600, "advanced": 2200}


def glossary(root: Path = SNAPSHOT) -> list[dict[str, Any]]:
    """The library's glossary (ADR-0062 § 3): English term, Uzbek term, aliases, note.

    Read from the snapshot; `slug` is the English term's, for `#anchor` links.
    """
    rows = json.loads((root / "glossary.json").read_text(encoding="utf-8"))
    out = []
    for row in rows:
        slug = "-".join(
            "".join(ch if ch.isalnum() else " " for ch in row["source"].lower()).split()
        )
        out.append(
            {
                "slug": slug,
                "term": row["uzbek"],
                "english": row["source"],
                "aliases": list(row.get("aliases") or []),
                "note": row.get("note") or "",
            }
        )
    return sorted(out, key=lambda r: r["term"].lower())


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class Report:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    kept_edited: list[str] = field(default_factory=list)
    published: list[str] = field(default_factory=list)
    not_published: list[str] = field(default_factory=list)


def load(root: Path = SNAPSHOT) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((root / "articles.json").read_text(encoding="utf-8"))
    allow = json.loads((root / "mechanical-allow.json").read_text(encoding="utf-8"))
    reviews = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((root / "reviews").glob("*.json"))
    }
    data["pending_mechanical"] = {
        row["id"] for row in allow["articles"] if row.get("status") == "pending"
    }
    data["reviews"] = reviews
    data["root"] = root
    return data


def _text(root: Path, lang: str, entry: dict[str, Any]) -> str:
    path = root / lang / str(entry["category"]) / f"{entry['slug']}.md"
    return path.read_text(encoding="utf-8")


def review_state(entry_id: str, data: dict[str, Any]) -> str:
    """`reviewed` only when the review said so and no mechanical row waits."""
    if entry_id in data["pending_mechanical"]:
        return Article.Review.PENDING
    final = (data["reviews"].get(entry_id) or {}).get("state")
    if final in (Article.Review.REVIEWED, Article.Review.DRAFT):
        return str(final)
    return Article.Review.PENDING


def _log(
    article: Article, data: dict[str, Any], entry_id: str, now: datetime, imported: bool
) -> None:
    """The import's own entry when the text came in or changed; the review's always."""
    rows: list[dict[str, Any]] = (
        [
            {
                "at": now,
                "actor": IMPORT_ACTOR,
                "stage": ArticleReview.Stage.IMPORT,
                "decision": "imported",
                "notes": (
                    f"cp.uz {data['cpuz_commit'][:7]} (snapshot {data['snapshot_commit'][:7]}), "
                    f"cp-algorithms {data['upstream_commit'][:7]}"
                ),
                "content_sha256": article.import_sha256,
            }
        ]
        if imported
        else []
    )
    for row in (data["reviews"].get(entry_id) or {}).get("log", []):
        at = parse_datetime(row["at"])
        if at is None:
            raise ValueError(f"{entry_id}: review date {row['at']!r}")
        rows.append(
            {
                "at": at,
                "actor": row["actor"],
                "stage": row["stage"],
                "decision": row["decision"],
                "notes": row.get("notes", ""),
                "content_sha256": row.get("content_sha256", ""),
            }
        )
    for row in rows:
        ArticleReview.objects.get_or_create(
            article=article,
            at=row["at"],
            stage=row["stage"],
            actor=row["actor"],
            defaults={k: row[k] for k in ("decision", "notes", "content_sha256")},
        )


def _fields(entry: dict[str, Any], data: dict[str, Any], body: str) -> dict[str, Any]:
    source = entry["source"]
    return {
        "slug": entry["slug"],
        "kind": Article.Kind.ALGORITHM,
        "title": entry["title"],
        "summary": entry["idea"][:300],
        "body": body,
        "locale": "uz",
        "difficulty": LEVEL_DIFFICULTY.get(entry["level"], 1600),
        "reading_minutes": max(1, len(body.split()) // 200),
        "category": entry["category"],
        "subcategory": entry["subcategory_uz"],
        "level": entry["level"],
        "order": entry["order"],
        "idea": entry["idea"],
        "complexity": entry["complexity"],
        "uses": entry["uses"],
        "source_title": source["title"],
        "source_url": source["url"],
        "source_commit": source["commit"],
        "source_license": source["license"],
        "import_commit": data["cpuz_commit"],
        "import_sha256": sha256(body),
        "translator": entry["translator"],
        "review_state": review_state(entry["id"], data),
    }


@transaction.atomic
def import_library(*, publish: bool = False, root: Path = SNAPSHOT) -> Report:
    data = load(root)
    report = Report()
    now = timezone.now()
    for entry in data["articles"]:
        body = _text(root, "uz", entry)
        wanted = _fields(entry, data, body)
        article = Article.objects.filter(source_ref=entry["id"]).first()
        if article is None:
            clash = Article.objects.filter(slug=entry["slug"]).first()
            if clash is not None:
                raise ValueError(
                    f"{entry['id']}: slug {entry['slug']!r} is taken by our own article {clash.pk}"
                )
            article = Article.objects.create(source_ref=entry["id"], **wanted)
            report.created.append(entry["id"])
        elif article.import_sha256 and sha256(article.body) != article.import_sha256:
            report.kept_edited.append(entry["id"])
            continue
        else:
            changed = [k for k, v in wanted.items() if getattr(article, k) != v]
            if changed:
                for key in changed:
                    setattr(article, key, wanted[key])
                article.save(update_fields=[*changed, "updated_at"])
                report.updated.append(entry["id"])
            else:
                report.unchanged.append(entry["id"])
        if not article.topics.exists():
            # Our topics, once: an editor's later choice is kept.
            article.topics.set(topic_ids(topics_for(entry["id"], entry["category"])))
        _translation(article, entry, root)
        _links(article, entry)
        _log(article, data, entry["id"], now, imported=entry["id"] not in report.unchanged)
        if publish:
            if article.review_state == Article.Review.REVIEWED:
                if not article.is_published:
                    article.is_published = True
                    article.save(update_fields=["is_published", "published_at", "updated_at"])
                report.published.append(entry["id"])
            else:
                report.not_published.append(entry["id"])
    return report


def _translation(article: Article, entry: dict[str, Any], root: Path) -> None:
    body = _text(root, "en", entry)
    row = ArticleTranslation.objects.filter(article=article, locale="en").first()
    if row is None:
        ArticleTranslation.objects.create(
            article=article,
            locale="en",
            title=entry["source"]["title"],
            body=body,
            import_sha256=sha256(body),
        )
        return
    if row.import_sha256 and sha256(row.body) != row.import_sha256:
        return  # edited here
    if row.body != body or row.title != entry["source"]["title"]:
        row.title = entry["source"]["title"]
        row.body = body
        row.import_sha256 = sha256(body)
        row.save()


def _links(article: Article, entry: dict[str, Any]) -> None:
    wanted = [
        (i, p["platform"], p["title"][:300], p["url"], p["key"], p["note"][:300])
        for i, p in enumerate(entry["practice"])
    ]
    current = list(
        article.external_links.order_by("order").values_list(
            "order", "platform", "title", "url", "key", "note"
        )
    )
    if current == wanted:
        return
    article.external_links.all().delete()
    ArticleExternalLink.objects.bulk_create(
        ArticleExternalLink(article=article, order=o, platform=pl, title=t, url=u, key=k, note=n)
        for o, pl, t, u, k, n in wanted
    )
