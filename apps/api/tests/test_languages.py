"""Judge language catalog and the `language` object every job carries (ADR-0022)."""

from __future__ import annotations

import importlib
import re
from typing import TYPE_CHECKING, Any

import pytest
from django.apps import apps
from django.core.exceptions import ValidationError

from hacks.services import _program
from judging.models import Attempt, CustomRun
from judging.provider import InMemoryJudgeProvider
from judging.services import build_job, enqueue_custom
from problems.languages import LANGUAGES, row_values
from problems.models import SOURCE_FILE_PATTERN, Language, Problem, ProblemLanguage

if TYPE_CHECKING:
    from types import ModuleType

SLUG = re.compile(r"^[a-z][a-z0-9]*$")
#: Created by seed_demo and fixtures, not by migrations.
FOUNDING = {"cpp23", "java21", "py313"}
#: One data migration per language group (ADR-0022).
GROUPS = [
    importlib.import_module("problems.migrations.0017_judge_languages_group1"),
    importlib.import_module("problems.migrations.0018_judge_languages_group2"),
    importlib.import_module("problems.migrations.0020_judge_languages_group3"),
]
KOTLIN_COLOURS = importlib.import_module("problems.migrations.0019_kotlin_colors_off")
GO_127 = importlib.import_module("problems.migrations.0043_go_127")


class TestCatalog:
    """The catalog is read by seed_demo, migrations and the image check alike."""

    def test_codes_are_unique_slugs(self) -> None:
        codes = [spec["code"] for spec in LANGUAGES]
        assert len(codes) == len(set(codes))
        assert all(SLUG.match(code) for code in codes), codes

    @pytest.mark.parametrize("spec", LANGUAGES, ids=lambda s: s["code"])
    def test_entry_is_complete(self, spec: dict[str, Any]) -> None:
        assert re.match(SOURCE_FILE_PATTERN, spec["source_file"]), spec["source_file"]
        assert spec["name"] and spec["version"]
        assert spec["run"] and all(isinstance(arg, str) for arg in spec["run"])
        assert all(isinstance(arg, str) for arg in spec["compile"])
        assert isinstance(spec["processes"], int) and spec["processes"] >= 1
        assert "{src}" in " ".join(spec["compile"] + spec["run"]), "the submission is never read"
        values = row_values(spec)
        assert values["compile_time_ms"] >= 1_000
        assert values["open_files"] == 0 or values["open_files"] >= 64

    def test_row_values_fill_every_judge_field(self) -> None:
        assert set(row_values(LANGUAGES[0])) == {
            "name",
            "version",
            "source_file",
            "compile_cmd",
            "run_cmd",
            "process_limit",
            "compile_time_ms",
            "proc_self",
            "open_files",
            "memory_overhead_kb",
        }


@pytest.mark.django_db
def test_seed_writes_the_catalog() -> None:
    for spec in LANGUAGES:
        Language.objects.update_or_create(code=spec["code"], defaults=row_values(spec))
    for spec in LANGUAGES:
        row = Language.objects.get(code=spec["code"])
        assert row.judge_spec() == {
            "code": spec["code"],
            "source_file": spec["source_file"],
            "compile": spec["compile"],
            "run": spec["run"],
            "proc_self": spec.get("proc_self", False),
            "open_files": spec.get("open_files", 0),
        }
        assert row.process_limit == spec["processes"]
        assert row.compile_time_ms == spec.get("compile_time_ms", 10_000)


@pytest.mark.django_db
def test_migrations_match_the_catalog() -> None:
    """Migrations freeze their rows; the catalog is what seed_demo and the image check read.
    A command changed in one place only would be judged differently in production."""
    for spec in LANGUAGES:
        if spec["code"] in FOUNDING:
            continue
        row = Language.objects.get(code=spec["code"])
        for field, value in row_values(spec).items():
            assert getattr(row, field) == value, (spec["code"], field)


@pytest.mark.django_db
@pytest.mark.parametrize("group", GROUPS, ids=lambda module: module.__name__.rsplit("_", 1)[-1])
class TestOpenProblemsGetNewLanguages:
    """Every group migration: problems open to all founding languages gain the new ones."""

    def _problem(self, slug: str, codes: list[str]) -> Problem:
        problem = Problem.objects.create(slug=slug, title=slug, statement="…", difficulty=800)
        for code in codes:
            ProblemLanguage.objects.create(
                problem=problem, language=Language.objects.get(code=code)
            )
        return problem

    def _codes(self, problem: Problem) -> set[str]:
        return set(problem.languages.values_list("language__code", flat=True))

    def test_open_restricted_and_unlisted(self, group: ModuleType) -> None:
        for code in sorted(FOUNDING):
            Language.objects.create(code=code, name=code, run_cmd=["{src}"])
        open_problem = self._problem("open", sorted(FOUNDING))
        python_only = self._problem("python-only", ["py313"])
        unlisted = self._problem("unlisted", [])

        group.add_languages(apps, None)

        added = {row["code"] for row in group.LANGUAGES}
        assert self._codes(open_problem) == FOUNDING | added
        assert self._codes(python_only) == {"py313"}
        # No list at all already means every language.
        assert self._codes(unlisted) == set()

    def test_without_founding_rows_nothing_is_granted(self, group: ModuleType) -> None:
        problem = self._problem("fresh", [])
        group.add_languages(apps, None)
        assert self._codes(problem) == set()


@pytest.mark.django_db
class TestKotlinColoursOff:
    """0019 changes a live row, so an admin's own command must survive it."""

    def _kotlin(self, compile_cmd: list[str]) -> Language:
        row = Language.objects.get(code="kotlin24")
        row.compile_cmd = compile_cmd
        row.save(update_fields=["compile_cmd"])
        return row

    def test_default_command_is_replaced_and_restored(self) -> None:
        row = self._kotlin(KOTLIN_COLOURS.BEFORE)
        KOTLIN_COLOURS.forwards(apps, None)
        row.refresh_from_db()
        assert row.compile_cmd == KOTLIN_COLOURS.AFTER
        KOTLIN_COLOURS.backwards(apps, None)
        row.refresh_from_db()
        assert row.compile_cmd == KOTLIN_COLOURS.BEFORE

    def test_edited_command_is_left_alone(self) -> None:
        row = self._kotlin(["/opt/kotlinc/bin/kotlinc", "-Werror", "{src}"])
        KOTLIN_COLOURS.forwards(apps, None)
        row.refresh_from_db()
        assert row.compile_cmd == ["/opt/kotlinc/bin/kotlinc", "-Werror", "{src}"]


@pytest.mark.django_db
class TestGoMovesTo127:
    """0043 renames a live row: its key, and an admin's own command, must survive it."""

    def test_row_is_renamed_in_place_and_restored(self) -> None:
        row = Language.objects.get(code="go127")
        GO_127.backwards(apps, None)
        old = Language.objects.get(pk=row.pk)
        assert (old.code, old.version) == ("go124", "1.24")
        assert not any("/usr/lib/go-1.27" in part for part in old.compile_cmd)
        assert any("/usr/lib/go-1.24" in part for part in old.compile_cmd)
        GO_127.forwards(apps, None)
        new = Language.objects.get(pk=row.pk)
        assert (new.code, new.version) == ("go127", "1.27")
        assert new.compile_cmd == row.compile_cmd
        assert new.run_cmd == row.run_cmd

    def test_what_points_at_go_still_does(self) -> None:
        row = Language.objects.get(code="go127")
        problem = Problem.objects.create(slug="go-only", title="go", statement="…", difficulty=800)
        ProblemLanguage.objects.create(problem=problem, language=row)
        GO_127.backwards(apps, None)
        GO_127.forwards(apps, None)
        assert list(problem.languages.values_list("language__code", flat=True)) == ["go127"]

    def test_edited_command_keeps_its_edit_and_finds_the_new_toolchain(self) -> None:
        GO_127.backwards(apps, None)
        row = Language.objects.get(code="go124")
        row.compile_cmd = [
            "/bin/sh",
            "-c",
            "GOROOT=/usr/lib/go-1.24 /usr/lib/go-1.24/bin/go vet {src}",
        ]
        row.save(update_fields=["compile_cmd"])
        GO_127.forwards(apps, None)
        row.refresh_from_db()
        assert row.code == "go127"
        assert row.compile_cmd == [
            "/bin/sh",
            "-c",
            "GOROOT=/usr/lib/go-1.27 /usr/lib/go-1.27/bin/go vet {src}",
        ]

    def test_an_existing_new_row_is_not_renamed_onto(self) -> None:
        # The catalog row is already there; a leftover `go124` must not collide with it.
        catalog_row = Language.objects.get(code="go127")
        leftover = Language.objects.create(
            code="go124",
            name="Go",
            version="1.24",
            compile_cmd=["/usr/lib/go-1.24/bin/go", "build", "{src}"],
            run_cmd=["{bin}"],
        )
        GO_127.forwards(apps, None)
        leftover.refresh_from_db()
        assert (leftover.code, leftover.version) == ("go124", "1.24")
        assert leftover.compile_cmd == ["/usr/lib/go-1.24/bin/go", "build", "{src}"]
        assert Language.objects.get(code="go127").pk == catalog_row.pk


class TestSourceFileValidation:
    @pytest.mark.parametrize("name", ["main.cpp", "Main.java", "main.fsx", "prog.test.ml"])
    def test_bare_names_pass(self, name: str, language: Language) -> None:
        language.source_file = name
        language.full_clean()

    @pytest.mark.parametrize(
        "name", ["../main.cpp", "a/main.cpp", ".bashrc", "main", "main.cpp\n", "main..cpp"]
    )
    def test_paths_are_refused(self, name: str, language: Language) -> None:
        language.source_file = name
        with pytest.raises(ValidationError):
            language.full_clean()


class TestJobsCarryLanguageSettings:
    """Every builder goes through `Language.judge_spec`; a job without the file
    name makes the judge write `main.txt`, and one without `proc_self` starts
    CoreCLR under a masked /proc, where it cannot start at all."""

    @pytest.fixture
    def csharp(self, db) -> Language:
        return Language.objects.create(
            code="cstest",
            name="C#",
            version="14",
            source_file="main.cs",
            compile_cmd=["dotnet", "csc.dll", "-out:{bin}.dll", "{src}"],
            run_cmd=["dotnet", "exec", "{bin}.dll"],
            process_limit=32,
            compile_time_ms=15_000,
            proc_self=True,
            open_files=256,
        )

    def test_submission_job(self, user, problem, csharp) -> None:
        attempt = Attempt.objects.create(
            user=user, problem=problem, language=csharp, source_code="class P {}"
        )
        job = build_job(attempt)
        assert job.language["source_file"] == "main.cs"
        assert job.language["proc_self"] is True
        assert job.language["open_files"] == 256
        assert job.limits["compile_time_ms"] == 15_000
        assert job.limits["processes"] == 32

    def test_custom_run_job(self, user, csharp, memory_judge: InMemoryJudgeProvider) -> None:
        run = CustomRun.objects.create(
            user=user, language=csharp, source_code="class P {}", stdin=""
        )
        enqueue_custom(run)
        job = memory_judge.jobs[-1]
        assert job.language["source_file"] == "main.cs"
        assert job.language["proc_self"] is True
        assert job.limits["compile_time_ms"] == 15_000

    def test_trusted_program(self, csharp) -> None:
        program = _program(csharp, "class P {}")
        assert program["source_file"] == "main.cs"
        assert program["proc_self"] is True
        assert program["open_files"] == 256
