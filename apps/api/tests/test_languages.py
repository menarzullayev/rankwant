"""Judge language catalog and the `language` object every job carries (ADR-0022)."""

from __future__ import annotations

import importlib
import re
from typing import Any

import pytest
from django.apps import apps
from django.core.exceptions import ValidationError

from hacks.services import _program
from judging.models import Attempt, CustomRun
from judging.provider import InMemoryJudgeProvider
from judging.services import build_job, enqueue_custom
from problems.languages import LANGUAGES, row_values
from problems.models import SOURCE_FILE_PATTERN, Language, Problem, ProblemLanguage

SLUG = re.compile(r"^[a-z][a-z0-9]*$")
#: Created by seed_demo and fixtures, not by migrations.
FOUNDING = {"cpp23", "java21", "py313"}
GROUP1 = importlib.import_module("problems.migrations.0017_judge_languages_group1")


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
class TestOpenProblemsGetNewLanguages:
    """Group 1 migration: problems open to all founding languages gain the new ones."""

    def _problem(self, slug: str, codes: list[str]) -> Problem:
        problem = Problem.objects.create(slug=slug, title=slug, statement="…", difficulty=800)
        for code in codes:
            ProblemLanguage.objects.create(
                problem=problem, language=Language.objects.get(code=code)
            )
        return problem

    def _codes(self, problem: Problem) -> set[str]:
        return set(problem.languages.values_list("language__code", flat=True))

    def test_open_restricted_and_unlisted(self) -> None:
        for code in sorted(FOUNDING):
            Language.objects.create(code=code, name=code, run_cmd=["{src}"])
        open_problem = self._problem("open", sorted(FOUNDING))
        python_only = self._problem("python-only", ["py313"])
        unlisted = self._problem("unlisted", [])

        GROUP1.add_languages(apps, None)

        group1 = {row["code"] for row in GROUP1.LANGUAGES}
        assert self._codes(open_problem) == FOUNDING | group1
        assert self._codes(python_only) == {"py313"}
        # No list at all already means every language.
        assert self._codes(unlisted) == set()

    def test_without_founding_rows_nothing_is_granted(self) -> None:
        problem = self._problem("fresh", [])
        GROUP1.add_languages(apps, None)
        assert self._codes(problem) == set()


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
