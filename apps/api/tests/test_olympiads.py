"""The olympiad archive (ADR-0062 § 2.6, stage 6)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.core.cache import cache
from django.core.management import CommandError, call_command
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from olympiads.importer import import_archive
from olympiads.models import Event, Participant, Result, Task
from problems.models import Problem

KEP_URL = "https://kep.uz/problems/2317"


def write(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def content(tmp_path: Path) -> Path:
    season = tmp_path / "seasons" / "2025-2026"
    write(
        season / "season.json",
        {
            "slug": "2025-2026",
            "title": "2025–2026 mavsumi",
            "start_date": "2025-09-01",
            "end_date": "2026-08-31",
            "routes": [{"code": "main", "title": "IOI yo'li", "kind": "official", "order": 10}],
        },
    )
    for slug, name in (("ali-valiyev", "Ali Valiyev"), ("vali-aliyev", "Vali Aliyev")):
        write(
            season / "participants" / f"{slug}.json",
            {"slug": slug, "full_name": name, "country_code": "UZB"},
        )
    write(
        season / "events" / "ioi-2026.json",
        {
            "slug": "ioi-2026",
            "code": "IOI26",
            "title": "IOI 2026",
            "type": "international",
            "start_date": "2026-08-09",
            "route_memberships": [{"route_code": "main", "order": 20, "label": "IOI"}],
            "resources": [{"type": "official_page", "title": "IOI", "url": "https://ioi2026.org"}],
            "results": [
                {
                    "participant": "ali-valiyev",
                    "rank": 50,
                    "score": 300,
                    "medal": "silver",
                    "order": 1,
                },
                {
                    "participant": "vali-aliyev",
                    "rank": 120,
                    "score": 200,
                    "medal": "bronze",
                    "order": 2,
                },
            ],
        },
    )
    write(
        season / "events" / "draft.json",
        {"slug": "draft", "title": "Draft", "publication_status": "draft"},
    )
    event = tmp_path / "problems" / "2025-2026" / "ioi-2026"
    write(event / "event.json", {"event_slug": "ioi-2026", "sets": ["day-1"]})
    write(
        event / "day-1" / "set.json",
        {"slug": "day-1", "title": "1-kun", "problems": ["kep-task", "ioi-task"]},
    )
    write(
        event / "day-1" / "kep-task" / "problem.json",
        {
            "slug": "kep-task",
            "code": "A",
            "title": "Deyarli anagrammalar",
            "links": [{"kind": "original", "title": "KEP", "url": KEP_URL, "platform": "KEP.uz"}],
        },
    )
    (event / "day-1" / "kep-task" / "statement.uz.md").write_text("Shart $a+b$.", encoding="utf-8")
    write(
        event / "day-1" / "ioi-task" / "problem.json",
        {
            "slug": "ioi-task",
            "code": "B",
            "title": "Koptok mashinasi",
            "links": [
                {
                    "kind": "original",
                    "title": "IOI",
                    "url": "https://ioinformatics.org/x.pdf",
                    "platform": "IOI",
                }
            ],
        },
    )
    (event / "day-1" / "ioi-task" / "statement.uz.md").write_text("Shart.", encoding="utf-8")
    return tmp_path


@pytest.mark.django_db
class TestImport:
    def test_the_archive_comes_in(self, content: Path) -> None:
        report = import_archive(content, "a" * 40)
        assert (
            report.seasons,
            report.events,
            report.participants,
            report.results,
            report.tasks,
        ) == (1, 1, 2, 2, 2)
        assert not Event.objects.filter(slug="draft").exists()
        assert Task.objects.get(slug="kep-task").from_kep
        assert not Task.objects.get(slug="ioi-task").from_kep

    def test_a_removal_survives_the_next_import(self, content: Path) -> None:
        import_archive(content, "a" * 40)
        Participant.objects.filter(slug="ali-valiyev").update(
            removed_at=timezone.now(), full_name=""
        )
        Task.objects.filter(slug="kep-task").update(removed_at=timezone.now())
        report = import_archive(content, "a" * 40)
        person = Participant.objects.get(slug="ali-valiyev")
        assert person.removed_at is not None and person.full_name == ""
        assert not Result.objects.filter(participant=person).exists()
        assert Task.objects.get(slug="kep-task").removed_at is not None
        assert "participant:ali-valiyev" in report.kept_removed

    def test_a_result_the_source_drops_goes(self, content: Path) -> None:
        import_archive(content, "a" * 40)
        path = content / "seasons" / "2025-2026" / "events" / "ioi-2026.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["results"] = doc["results"][:1]
        path.write_text(json.dumps(doc), encoding="utf-8")
        import_archive(content, "a" * 40)
        assert list(Result.objects.values_list("participant__slug", flat=True)) == ["ali-valiyev"]

    def test_the_command_wants_a_content_directory(self, tmp_path: Path) -> None:
        with pytest.raises(CommandError, match="no seasons"):
            call_command("import_olympiads", source=str(tmp_path), commit="x")


@pytest.mark.django_db
class TestApi:
    @pytest.fixture(autouse=True)
    def archive(self, content: Path) -> None:
        cache.clear()
        import_archive(content, "a" * 40)

    def test_seasons_list_their_events(self) -> None:
        body = APIClient().get(reverse("olympiad-seasons")).json()
        assert body[0]["slug"] == "2025-2026" and body[0]["routes"][0]["code"] == "main"
        event = body[0]["events"][0]
        assert (event["slug"], event["task_count"], event["result_count"]) == ("ioi-2026", 2, 2)

    def test_an_event_has_its_rounds_and_results(self) -> None:
        body = APIClient().get(reverse("olympiad-event", args=["ioi-2026"])).json()
        assert [t["slug"] for t in body["sets"][0]["tasks"]] == ["kep-task", "ioi-task"]
        assert [r["full_name"] for r in body["results"]] == ["Ali Valiyev", "Vali Aliyev"]
        assert body["resources"][0]["url"] == "https://ioi2026.org"

    def test_a_task_links_to_our_copy_by_its_source(self) -> None:
        Problem.objects.create(
            slug="anagram",
            title="Anagram",
            code=7,
            statement="x",
            difficulty=1200,
            is_public=True,
            source_url=KEP_URL,
        )
        cache.clear()
        body = APIClient().get(reverse("olympiad-task", args=["ioi-2026", "kep-task"])).json()
        assert body["from_kep"] is True and body["statement"] == "Shart $a+b$."
        assert body["practice_here"] == [{"slug": "anagram", "code": 7, "title": "Anagram"}]

    def test_a_participant_page_lists_results(self) -> None:
        body = APIClient().get(reverse("olympiad-participant", args=["ali-valiyev"])).json()
        assert body["full_name"] == "Ali Valiyev"
        assert body["results"][0]["medal"] == "silver"

    def test_a_removed_person_and_statement_are_gone(self) -> None:
        Participant.objects.filter(slug="ali-valiyev").update(
            removed_at=timezone.now(), full_name=""
        )
        Task.objects.filter(slug="kep-task").update(removed_at=timezone.now())
        client = APIClient()
        assert client.get(reverse("olympiad-participant", args=["ali-valiyev"])).status_code == 404
        assert (
            client.get(reverse("olympiad-task", args=["ioi-2026", "kep-task"])).status_code == 404
        )
        body = client.get(reverse("olympiad-event", args=["ioi-2026"])).json()
        assert [r["participant"] for r in body["results"]] == ["vali-aliyev"]
        assert [t["slug"] for t in body["sets"][0]["tasks"]] == ["ioi-task"]
        season = client.get(reverse("olympiad-seasons")).json()[0]["events"][0]
        assert (season["task_count"], season["result_count"]) == (1, 1)


def test_the_repository_keeps_no_personal_olympiad_data() -> None:
    """Profiles and KEP statements are imported from the host, never vendored."""
    api = Path(__file__).resolve().parent.parent
    assert not list(api.rglob("participants/*.json"))
    assert not list(api.rglob("statement.uz.md"))
