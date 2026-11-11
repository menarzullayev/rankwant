"""The Abramyan import (ADR-0060 § 2.5–2.6), on a two-problem package."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from content.models import Roadmap
from core.models import User
from judging.models import Attempt
from problems import abramyan
from problems.languages import LANGUAGES, row_values
from problems.management.commands.verify_abramyan import ACCOUNT, EMPTY
from problems.models import Language, Problem, ProblemTranslation, ReferenceSolution, Topic

FILE_UZ = abramyan.FILE_SENTENCES["uz"][0][0]


def _statement(text: str) -> dict[str, str]:
    return {
        "legend": f'<p>{text} <span class="math-tex">\\(a &lt; b\\)</span>.</p>',
        "input": "<p>Kirish</p>",
        "output": "<p>Chiqish</p>",
        "note": "",
    }


def _task(code: str, section: str, order: int, checker: str, rework: bool, legend: str) -> dict:
    return {
        "code": code,
        "section": section,
        "order": order,
        "title": {lang: f"{code} [Nom {lang}]" for lang in ("uz", "ru", "en", "qq")},
        "statement_html": {lang: _statement(legend) for lang in ("uz", "ru", "en", "qq")},
        "checker": checker,
        "needs_file_io_rework": rework,
    }


@pytest.fixture
def package(tmp_path: Path) -> Path:
    tasks = [
        _task("Begin1", "Begin", 1, "real_eps_1e-6", False, "Kvadrat"),
        _task("File1", "File", 1, "exact", True, FILE_UZ),
    ]
    plan = {
        "slug": "abramyan-masalalar",
        "name": {"uz": "Abramyan", "ru": "Абрамян", "en": "Abramyan", "qq": "Abramyan"},
        "description": {"uz": "x", "ru": "x", "en": "x", "qq": "x"},
        "sections": [
            {
                "key": "Begin",
                "title": {"uz": "Boshlang'ich", "ru": "Начало", "en": "Begin", "qq": "Baslanıw"},
                "description": {"uz": "40 ta masala. Mashg'ulot contesti: #4126"},
                "tasks": ["Begin1"],
            },
            {"key": "File", "title": {"uz": "Fayllar"}, "description": {}, "tasks": ["File1"]},
        ],
    }
    (tmp_path / "manifest.json").write_text(
        json.dumps({"tasks": tasks, "study_plan": plan}), encoding="utf-8"
    )
    for task in tasks:
        folder = tmp_path / "tests" / task["code"]
        folder.mkdir(parents=True)
        for order in (1, 2, 3):
            (folder / f"000{order}.in").write_text(f"{order}\n", encoding="utf-8")
            (folder / f"000{order}.out").write_text(f"{order * 4}\n", encoding="utf-8")
    (tmp_path / "solutions").mkdir()
    for task in tasks:
        (tmp_path / "solutions" / f"{task['code']}.py").write_text(
            "print(int(input()) * 4)\n", encoding="utf-8"
        )
    return tmp_path


@pytest.fixture
def languages(db) -> None:
    for spec in LANGUAGES:
        Language.objects.update_or_create(code=spec["code"], defaults=row_values(spec))
    for slug in ("oddiy", "math", "fayllar"):
        Topic.objects.get_or_create(slug=slug, defaults={"name_uz": slug})


def _run(package: Path, **extra: str) -> None:
    call_command(
        "import_abramyan", "--package", str(package), "--no-storage", "--no-images", **extra
    )


@pytest.mark.django_db
class TestImport:
    def test_unofficial_drafts_without_numbers(self, package, languages, user) -> None:
        _run(package, author=user.username)
        begin = Problem.objects.get(slug="begin1")
        assert (begin.is_public, begin.is_official, begin.code) == (False, False, None)
        assert begin.title == "Begin1. Nom uz"
        assert begin.statement == "Kvadrat $a < b$."
        assert (begin.checker_type, begin.real_tolerance) == ("real", 1e-6)
        assert (begin.time_limit_ms, begin.memory_limit_kb) == (1000, 65536)
        assert begin.source == abramyan.SOURCE
        assert list(begin.authors.all()) == [user]
        assert sorted(begin.topics.values_list("slug", flat=True)) == ["math", "oddiy"]
        assert set(
            ProblemTranslation.objects.filter(problem=begin).values_list("locale", flat=True)
        ) == {
            "ru",
            "en",
            "kaa",
        }
        assert [(t.order, t.is_sample) for t in begin.tests.all()] == [
            (1, True),
            (2, True),
            (3, False),
        ]

    def test_file_problems_use_input_and_output_files(self, package, languages) -> None:
        _run(package)
        file1 = Problem.objects.get(slug="file1")
        assert file1.io_mode == "both" and file1.checker_type == "standard"
        assert "input.txt" in file1.statement and "o'rniga" not in file1.statement
        assert ReferenceSolution.objects.get(problem=file1).source.startswith(
            abramyan.FILE_PREAMBLE
        )

    def test_the_study_plan(self, package, languages) -> None:
        _run(package)
        plan = Roadmap.objects.get(slug="abramyan-masalalar")
        assert not plan.is_published
        assert plan.translations["kaa"]["title"] == "Abramyan"
        assert plan.description == abramyan.PLAN_DESCRIPTION["uz"]
        sections = list(plan.sections.order_by("order"))
        assert [s.title for s in sections] == ["Boshlang'ich", "Fayllar"]
        assert sections[0].description == "40 ta masala."
        steps = plan.steps.order_by("order")
        assert [(s.order, s.problem and s.problem.slug, s.section_id) for s in steps] == [
            (1, "begin1", sections[0].pk),
            (2, "file1", sections[1].pk),
        ]

    def test_a_second_run_changes_nothing(self, package, languages) -> None:
        _run(package)
        counts = (
            Problem.objects.count(),
            ProblemTranslation.objects.count(),
            Roadmap.objects.count(),
        )
        _run(package)
        assert counts == (
            Problem.objects.count(),
            ProblemTranslation.objects.count(),
            Roadmap.objects.count(),
        )

    def test_a_rerun_never_unpublishes(self, package, languages) -> None:
        _run(package)
        Problem.objects.filter(slug="begin1").update(is_public=True)
        _run(package)
        assert Problem.objects.get(slug="begin1").is_public


@pytest.mark.django_db
class TestPublish:
    def _verify(self, verdicts: dict[str, tuple[str, str]]) -> None:
        account, _ = User.objects.get_or_create(username=ACCOUNT)
        language = Language.objects.get(code="py313")
        for slug, (reference, empty) in verdicts.items():
            problem = Problem.objects.get(slug=slug)
            Attempt.objects.create(
                user=account, problem=problem, language=language, source_code="x", verdict=reference
            )
            Attempt.objects.create(
                user=account, problem=problem, language=language, source_code=EMPTY, verdict=empty
            )

    def test_refuses_until_every_problem_is_green(self, package, languages) -> None:
        _run(package)
        self._verify({"begin1": ("AC", "WA"), "file1": ("WA", "WA")})
        with pytest.raises(CommandError, match="file1"):
            call_command("publish_abramyan")
        assert not Problem.objects.filter(is_public=True).exists()

    def test_an_empty_program_that_passes_is_not_green(self, package, languages) -> None:
        _run(package)
        self._verify({"begin1": ("AC", "AC"), "file1": ("AC", "WA")})
        with pytest.raises(CommandError, match="begin1"):
            call_command("publish_abramyan")

    def test_publishes_all_together_without_numbers(self, package, languages) -> None:
        _run(package)
        self._verify({"begin1": ("AC", "WA"), "file1": ("AC", "RE_EXIT")})
        call_command("publish_abramyan")
        rows = Problem.objects.filter(source=abramyan.SOURCE)
        assert rows.filter(is_public=True).count() == 2
        assert not rows.exclude(code=None).exists()
        assert Roadmap.objects.get(slug="abramyan-masalalar").is_published


class TestPureRules:
    def test_title_and_math(self) -> None:
        assert abramyan.code_title("Begin1 [Kvadrat perimetri]") == "Begin1. Kvadrat perimetri"
        assert abramyan.to_markdown('<p><span class="math-tex">\\(x_1 \\le 2\\)</span></p>') == (
            "$x_1 \\le 2$"
        )

    @pytest.mark.parametrize("lang", ["uz", "ru", "en", "qq"])
    def test_every_adaptation_sentence_becomes_file_io(self, lang: str) -> None:
        for old, new in abramyan.FILE_SENTENCES[lang]:
            out = abramyan.to_file_io(f"Boshi. {old}", lang)
            assert (old not in out and new in out and "input.txt" in out) or "output.txt" in out
        assert abramyan.FILE_NOTE[lang] in abramyan.to_file_io("Faylsiz matn.", lang)

    def test_file_solution_keeps_future_imports_first(self) -> None:
        source = "from __future__ import annotations\nprint(1)\n"
        out = abramyan.file_solution(source)
        assert out.startswith("from __future__ import annotations\n" + abramyan.FILE_PREAMBLE)

    def test_difficulty_grows_through_a_section_and_stays_on_the_scale(self) -> None:
        tasks = [{"code": f"Array{i}", "section": "Array", "order": i} for i in range(1, 11)]
        sizes = {f"Array{i}": i for i in range(1, 11)}
        values = [
            e.difficulty
            for e in sorted(abramyan.estimate(tasks, sizes).values(), key=lambda e: e.position)
        ]
        assert values == sorted(values)
        assert values[0] == 1000 and values[-1] == 1500
        assert all(v % 100 == 0 for v in values)

    def test_plan_text_drops_the_contest_number(self) -> None:
        assert abramyan.plan_text("40 ta masala. Mashg'ulot contesti: #4126") == "40 ta masala."
