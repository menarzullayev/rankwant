"""The cp.uz algorithms library import (ADR-0062, stage 1)."""

from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path

import pytest
from django.apps import apps as django_apps

from content.cpuz import SNAPSHOT, import_library, sha256
from content.exercise_keys import exercise_key
from content.models import (
    Article,
    ArticleExternalLink,
    ArticleReview,
    ArticleTranslation,
    Roadmap,
    RoadmapStep,
)

ENTRIES = json.loads((SNAPSHOT / "articles.json").read_text(encoding="utf-8"))["articles"]


def small_snapshot(tmp_path: Path, ids: list[str], reviews: dict | None = None) -> Path:
    """A copy of the vendored snapshot holding only `ids`."""
    data = json.loads((SNAPSHOT / "articles.json").read_text(encoding="utf-8"))
    data["articles"] = [a for a in data["articles"] if a["id"] in ids]
    for a in data["articles"]:
        for lang in ("uz", "en"):
            target = tmp_path / lang / a["category"] / f"{a['slug']}.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SNAPSHOT / lang / a["category"] / f"{a['slug']}.md", target)
    (tmp_path / "articles.json").write_text(json.dumps(data), encoding="utf-8")
    allow = json.loads((SNAPSHOT / "mechanical-allow.json").read_text(encoding="utf-8"))
    allow["articles"] = [row for row in allow["articles"] if row["id"] in ids]
    (tmp_path / "mechanical-allow.json").write_text(json.dumps(allow), encoding="utf-8")
    for ref, review in (reviews or {}).items():
        (tmp_path / "reviews").mkdir(exist_ok=True)
        (tmp_path / "reviews" / f"{ref}.json").write_text(json.dumps(review), encoding="utf-8")
    return tmp_path


def clean_id() -> str:
    """An article whose code and formulas already match the original."""
    allow = json.loads((SNAPSHOT / "mechanical-allow.json").read_text(encoding="utf-8"))
    pending = {row["id"] for row in allow["articles"]}
    return str(next(a["id"] for a in ENTRIES if a["id"] not in pending))


@pytest.mark.django_db
class TestImport:
    def test_the_whole_library_comes_in_unpublished(self) -> None:
        report = import_library()
        assert len(report.created) == len(ENTRIES) == 163
        imported = Article.objects.exclude(source_ref="")
        assert imported.count() == 163
        assert not imported.filter(is_published=True).exists()
        assert set(imported.values_list("kind", flat=True)) == {Article.Kind.ALGORITHM}
        assert imported.filter(category="graph").count() == 47
        assert set(imported.values_list("level", flat=True)) == {
            "beginner",
            "intermediate",
            "advanced",
        }
        binary_exp = Article.objects.get(source_ref="algebra--binary-exp")
        assert binary_exp.slug == "binary-exp"
        assert binary_exp.source_url == "https://cp-algorithms.com/algebra/binary-exp.html"
        assert binary_exp.source_license == "CC-BY-SA-4.0"
        assert binary_exp.import_sha256 == sha256(binary_exp.body)
        # The English original is the `en` version (§ 2.4).
        assert ArticleTranslation.objects.filter(locale="en").count() == 163
        assert binary_exp.translations.get(locale="en").title == "Binary Exponentiation"
        # Practice links keep their judge-free key (§ 2.5).
        assert ArticleExternalLink.objects.count() == 885
        assert binary_exp.external_links.filter(key="uva:3671").exists()
        assert ArticleReview.objects.filter(stage="import").count() == 163

    def test_a_second_run_changes_nothing(self) -> None:
        import_library()
        reviews = ArticleReview.objects.count()
        report = import_library()
        assert report.created == report.updated == report.kept_edited == []
        assert len(report.unchanged) == 163
        assert ArticleReview.objects.count() == reviews

    def test_an_article_edited_here_is_kept(self) -> None:
        import_library()
        article = Article.objects.get(source_ref="algebra--binary-exp")
        article.body += "\n\nTahrir."
        article.save()
        report = import_library()
        assert report.kept_edited == ["algebra--binary-exp"]
        article.refresh_from_db()
        assert article.body.endswith("Tahrir.")

    def test_publishing_takes_only_reviewed_articles(self, tmp_path: Path) -> None:
        pending = json.loads((SNAPSHOT / "mechanical-allow.json").read_text(encoding="utf-8"))
        waiting = pending["articles"][0]["id"]
        reviewed = clean_id()
        root = small_snapshot(
            tmp_path,
            [waiting, reviewed],
            reviews={
                reviewed: {
                    "state": "reviewed",
                    "log": [
                        {
                            "at": "2026-11-12T10:00:00+05:00",
                            "actor": "agent",
                            "stage": "technical",
                            "decision": "passed",
                            "notes": "",
                        }
                    ],
                },
                # Said reviewed, but its code still waits for the mechanical check.
                waiting: {"state": "reviewed", "log": []},
            },
        )
        report = import_library(publish=True, root=root)
        assert report.published == [reviewed]
        assert report.not_published == [waiting]
        assert Article.objects.get(source_ref=reviewed).is_published
        assert not Article.objects.get(source_ref=waiting).is_published
        assert Article.objects.get(source_ref=reviewed).reviews.filter(stage="technical").exists()

    def test_our_own_article_with_the_same_slug_stops_the_import(self, tmp_path: Path) -> None:
        Article.objects.create(slug="binary-exp", title="Bizniki", body="x")
        root = small_snapshot(tmp_path, ["algebra--binary-exp"])
        with pytest.raises(ValueError, match="taken by our own article"):
            import_library(root=root)


@pytest.mark.parametrize(
    ("url", "key"),
    [
        ("https://codeforces.com/contest/1234/problem/a", "codeforces:1234A"),
        ("https://codeforces.com/problemset/problem/1234/A", "codeforces:1234A"),
        ("http://codeforces.com/gym/100001/problem/B", "codeforces-gym:100001B"),
        ("https://www.spoj.com/problems/aggrcow/", "spoj:AGGRCOW"),
        (
            "http://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem=3671",
            "uva:3671",
        ),
        ("https://cses.fi/problemset/task/1068", "cses:1068"),
        ("https://www.codechef.com/problems/abc", "codechef:ABC"),
        ("https://leetcode.com/problems/Two-Sum/description/", "leetcode:two-sum"),
        ("https://acm.timus.ru/problem.aspx?space=1&num=1001", "timus:1001"),
        ("https://example.org/Some/Path/", "example.org:/some/path"),
    ],
)
def test_exercise_keys_are_judge_independent(url: str, key: str) -> None:
    assert exercise_key(url) == key


@pytest.mark.django_db
def test_the_old_binary_search_article_is_deleted() -> None:
    """Owner decision ⑨: ours goes, no redirect; a step left empty goes with it."""
    migration = importlib.import_module("content.migrations.0005_drop_ikkilik_qidiruv")
    old = Article.objects.create(slug="ikkilik-qidiruv", title="Ikkilik qidiruv", body="x")
    keep = Article.objects.create(slug="boshqa", title="Boshqa", body="x")
    roadmap = Roadmap.objects.create(slug="yol", title="Yo'l")
    RoadmapStep.objects.create(roadmap=roadmap, order=1, article=old)
    RoadmapStep.objects.create(roadmap=roadmap, order=2, article=keep)
    migration.drop(django_apps, None)
    assert not Article.objects.filter(slug="ikkilik-qidiruv").exists()
    assert list(roadmap.steps.values_list("order", flat=True)) == [2]
