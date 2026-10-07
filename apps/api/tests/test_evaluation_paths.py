"""The three ways of grading besides the standard checker, and the pairs of
modes the judge cannot grade (`problems/evaluation.py`).

The reference problems (`problems/reference_problems.py`) are checked twice
here without a judge: that they install as complete, publishable problems,
and that every listed submission earns the verdict and score written next
to it when the problem's own checker, scorer or interactor is run on it.
The same table is submitted to the real judge by `tools/e2e_evaluation_paths.py`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from judging.models import Attempt
from judging.services import apply_result, build_job
from problems import readiness, release, taskkinds
from problems.evaluation import (
    EVALUATION_MODE_INVALID,
    combination_error,
    evaluation_error,
    subtask_error,
    task_kind_error,
)
from problems.models import Language, Problem, ProblemLanguage, ReferenceSolution, Subtask
from problems.reference_problems import (
    COINS,
    GUESS,
    MAXPAIR,
    PAIR,
    REFERENCES,
    Reference,
    install,
)
from ratings.models import UserSolvedProblem

pytestmark = pytest.mark.django_db

STDIO, BOTH = Problem.IoMode.STDIO, Problem.IoMode.BOTH


# ── which pairs can be graded ────────────────────────────────────────────────


class TestCombinations:
    @pytest.mark.parametrize(
        ("io_mode", "checker"),
        [
            (STDIO, "standard"),
            (STDIO, "special"),
            (STDIO, "interactive"),
            (STDIO, "scorer"),
            (BOTH, "standard"),
        ],
    )
    def test_a_pair_the_judge_implements_is_accepted(self, io_mode: str, checker: str) -> None:
        assert combination_error(io_mode, checker) is None

    @pytest.mark.parametrize("checker", ["special", "interactive", "scorer"])
    def test_file_io_with_a_checker_program_is_refused(self, checker: str) -> None:
        error = combination_error(BOTH, checker)
        assert error is not None
        assert "io_mode 'both'" in error

    def test_the_message_says_why(self) -> None:
        assert "receives stdout only" in (combination_error(BOTH, "special") or "")
        assert "input.txt is never written" in (combination_error(BOTH, "interactive") or "")

    @pytest.mark.parametrize("checker", ["interactive", "scorer"])
    def test_subtasks_are_refused_where_they_would_never_score(self, checker: str) -> None:
        assert subtask_error(checker, True) is not None
        assert subtask_error(checker, False) is None

    @pytest.mark.parametrize("checker", ["standard", "special"])
    def test_subtasks_are_fine_where_they_score(self, checker: str) -> None:
        assert subtask_error(checker, True) is None


@pytest.fixture
def staff_client(db) -> APIClient:
    client = APIClient()
    client.force_authenticate(User.objects.create_user("staff1", password="x", is_staff=True))
    return client


@pytest.fixture
def python(db) -> Language:
    return Language.objects.create(
        code="py313", name="Python", version="3.13", run_cmd=["python3", "{src}"]
    )


class TestRefusedWhereItIsTyped:
    def test_the_staff_api_refuses_a_checker_on_a_file_io_problem(
        self, staff_client: APIClient, problem: Problem, python: Language
    ) -> None:
        Problem.objects.filter(pk=problem.pk).update(io_mode=BOTH)
        response = staff_client.patch(
            reverse("staff-problem-detail", args=[problem.slug]),
            {"checker_type": "special", "checker_source": "x", "checker_language": python.code},
            format="json",
        )
        assert response.status_code == 400, response.content
        assert EVALUATION_MODE_INVALID in json.dumps(response.json())
        problem.refresh_from_db()
        assert problem.checker_type == "standard"

    def test_the_same_edit_on_a_stdio_problem_goes_through(
        self, staff_client: APIClient, problem: Problem, python: Language
    ) -> None:
        response = staff_client.patch(
            reverse("staff-problem-detail", args=[problem.slug]),
            {"checker_type": "special", "checker_source": "x", "checker_language": python.code},
            format="json",
        )
        assert response.status_code == 200, response.content

    def test_a_scorer_cannot_be_put_on_a_problem_with_subtasks(
        self, staff_client: APIClient, problem: Problem, python: Language
    ) -> None:
        Subtask.objects.create(problem=problem, order=1, points=100)
        response = staff_client.patch(
            reverse("staff-problem-detail", args=[problem.slug]),
            {"checker_type": "scorer", "checker_source": "x", "checker_language": python.code},
            format="json",
        )
        assert response.status_code == 400
        assert "subtasks" in json.dumps(response.json())

    def test_the_model_refuses_it_too(self, problem: Problem) -> None:
        # The Django admin can set `io_mode`; the staff API cannot.
        problem.io_mode, problem.checker_type = BOTH, "interactive"
        with pytest.raises(ValidationError) as caught:
            problem.clean()
        assert "checker_type" in caught.value.message_dict


class TestRefusedBeforeItIsGraded:
    def _invalid(self, problem: Problem, python: Language) -> Problem:
        Problem.objects.filter(pk=problem.pk).update(
            io_mode=BOTH, checker_type="special", checker_source="x", checker_language=python
        )
        problem.refresh_from_db()
        return problem

    def test_readiness_does_not_advance(self, problem: Problem, python: Language) -> None:
        broken = self._invalid(problem, python)
        error = readiness.requirement_error(broken, Problem.Readiness.CHECKER_VALIDATED)
        assert error is not None
        assert error.startswith("S2: io_mode 'both'")

    def test_the_release_report_names_the_gate(self, problem: Problem, python: Language) -> None:
        broken = self._invalid(problem, python)
        assert EVALUATION_MODE_INVALID in release.blocking_codes(broken)
        with pytest.raises(Exception) as caught:
            release.assert_publishable(broken)
        assert EVALUATION_MODE_INVALID in str(caught.value)

    def test_a_valid_problem_passes_the_gate(self, problem: Problem) -> None:
        assert release.evaluation_gate(problem).passed
        assert evaluation_error(problem) is None


# ── the reference problems ───────────────────────────────────────────────────


@pytest.fixture
def stored(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Object storage as a dictionary."""
    data: dict[str, str] = {}

    def put(key: str, content: str) -> str:
        data[f"s3://rankwant/{key}"] = content
        return f"s3://rankwant/{key}"

    monkeypatch.setattr("problems.storage.put_test_data", put)
    monkeypatch.setattr("problems.storage.get_test_data", lambda ref: data[ref])
    monkeypatch.setattr("problems.storage.ensure_bucket", lambda: None)
    return data


class TestInstall:
    def test_installs_one_problem_for_each_way_of_grading(self, stored: dict[str, str]) -> None:
        problems = install()
        assert [p.checker_type for p in problems] == [
            "special",
            "interactive",
            "scorer",
            "standard",
        ]
        assert [p.task_kind for p in problems] == ["program", "program", "program", "function"]
        for problem in problems:
            assert problem.is_public, problem.slug
            assert problem.code, problem.slug
            assert problem.io_mode == STDIO

    def test_each_one_is_complete(self, stored: dict[str, str]) -> None:
        for problem in install():
            assert readiness.has_hidden_test(problem), problem.slug
            assert readiness.checker_ready(problem), problem.slug
            assert ReferenceSolution.objects.filter(problem=problem).exists(), problem.slug
            assert evaluation_error(problem) is None
            # The static release gates: statement, test groups, grading modes.
            for gate in (release.statement_gate, release.test_group_gate, release.evaluation_gate):
                result = gate(problem)
                assert result.passed, (problem.slug, result.code, result.detail)
            # ...and readiness may advance as far as a judge-less check allows.
            assert (
                readiness.requirement_error(problem, Problem.Readiness.REF_SOLUTION_VERIFIED)
                is None
            )

    def test_installing_twice_changes_nothing(self, stored: dict[str, str]) -> None:
        first = {p.slug: (p.pk, p.code, p.tests.count()) for p in install()}
        second = {p.slug: (p.pk, p.code, p.tests.count()) for p in install()}
        assert first == second
        assert Problem.objects.filter(slug__startswith="ref-").count() == len(REFERENCES)

    def test_a_draft_install_stays_private(self, stored: dict[str, str]) -> None:
        assert not any(p.is_public for p in install(publish=False))

    def test_the_job_carries_the_program_the_judge_needs(
        self, stored: dict[str, str], user: User
    ) -> None:
        install()
        python = Language.objects.get(code="py313")
        seen = {}
        for ref in REFERENCES:
            problem = Problem.objects.get(slug=ref.slug)
            attempt = Attempt.objects.create(
                user=user, problem=problem, language=python, source_code=ref.reference
            )
            job = json.loads(build_job(attempt).to_json())
            seen[ref.checker_type] = job["checker"]
            assert job["mode"] == "acm"
            assert not job.get("io")
            assert len(job["tests"]) == len(ref.tests)
        assert seen["special"]["program"]["source"] == PAIR.checker
        assert seen["scorer"]["program"]["source"] == COINS.checker
        assert seen["interactive"]["interactor"]["source"] == GUESS.interactor
        assert "program" not in seen["interactive"]


# ── what each listed submission earns ────────────────────────────────────────


def _run(source: str, stdin: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    path = tmp_path / "solution.py"
    path.write_text(source, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(path)], input=stdin, capture_output=True, text=True, timeout=20
    )


def _checker(ref: Reference, tmp_path: Path, test_in: str, output: str, answer: str):  # type: ignore[no-untyped-def]
    for name, body in (("in", test_in), ("out", output), ("ans", answer)):
        (tmp_path / f"checker.{name}").write_text(body, encoding="utf-8")
    checker = tmp_path / "checker.py"
    checker.write_text(ref.checker, encoding="utf-8")
    return subprocess.run(
        [
            sys.executable,
            str(checker),
            *(str(tmp_path / f"checker.{n}") for n in ("in", "out", "ans")),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )


def grade_with_checker(ref: Reference, source: str, tmp_path: Path) -> tuple[str, int]:
    """The judge's rules for `special` and `scorer`, without a sandbox.

    ACM mode stops at the first failed test; a scorer's result is the mean
    over all tests and is `AC` only at the full score (`judge.go`).
    """
    total, worst = 0, "AC"
    for test_in, answer, _group in ref.tests:
        output = _run(source, test_in, tmp_path).stdout
        result = _checker(ref, tmp_path, test_in, output, answer)
        if ref.checker_type == "special":
            if result.returncode != 0:
                return "WA", 0
            continue
        score = min(100, int(float(result.stdout.split()[-1])))
        if score <= 0:
            worst = "WA"
            break
        total += score
    if ref.checker_type == "special":
        return "AC", 100
    mean = total // len(ref.tests)
    if worst == "AC" and mean < 100:
        worst = "PARTIAL" if mean > 0 else "WA"
    elif worst != "AC" and mean > 0:
        worst = "PARTIAL"
    return worst, mean


def grade_interactive(ref: Reference, source: str, tmp_path: Path) -> str:
    """One dialogue between the solution and the interactor, over pipes."""
    solution, interactor = tmp_path / "solution.py", tmp_path / "interactor.py"
    solution.write_text(source, encoding="utf-8")
    interactor.write_text(ref.interactor, encoding="utf-8")
    judge = subprocess.Popen(
        [sys.executable, str(interactor)], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    solver = subprocess.Popen(
        [sys.executable, str(solution)],
        stdin=judge.stdout,
        stdout=judge.stdin,
        stderr=subprocess.DEVNULL,
    )
    # Ours are copies: each side must see the end of input when the other exits.
    assert judge.stdin is not None and judge.stdout is not None
    judge.stdin.close()
    judge.stdout.close()
    try:
        judge.wait(timeout=4)
        solver.wait(timeout=4)
    except subprocess.TimeoutExpired:
        judge.kill()
        solver.kill()
        return "IDLENESS"
    return "AC" if judge.returncode == 0 else "WA"


class TestReferenceSubmissions:
    @pytest.mark.parametrize("ref", [PAIR, COINS], ids=lambda ref: ref.checker_type)
    def test_the_checker_gives_each_submission_what_the_table_says(
        self, ref: Reference, tmp_path: Path
    ) -> None:
        for case in ref.cases:
            assert grade_with_checker(ref, case.source, tmp_path) == (case.verdict, case.score), (
                case.name
            )

    def test_the_interactor_gives_each_dialogue_what_the_table_says(self, tmp_path: Path) -> None:
        for case in GUESS.cases:
            assert grade_interactive(GUESS, case.source, tmp_path) == case.verdict, case.name

    def test_a_special_checker_is_really_deciding(self, tmp_path: Path) -> None:
        # The accepted answer differs from the jury's wherever the sum
        # allows a second pair (2 has only `1 1`): an equality comparison
        # would have rejected it.
        other = next(c for c in PAIR.cases if "another valid" in c.name)
        differing = [
            test_in
            for test_in, answer, _group in PAIR.tests
            if _run(other.source, test_in, tmp_path).stdout.split() != answer.split()
        ]
        assert len(differing) == len(PAIR.tests) - 1

    def test_the_scorer_tells_three_qualities_apart(self) -> None:
        scores = sorted({case.score for case in COINS.cases})
        assert scores[0] == 0 and scores[-1] == 100
        assert len(scores) >= 4

    def test_the_jurys_coin_answers_are_the_fewest(self) -> None:
        for test_in, answer, _group in COINS.tests:
            count, *coins = map(int, answer.split())
            assert count == len(coins) and sum(coins) == int(test_in)


# ── the result on its way to the API ─────────────────────────────────────────


class TestResultIsStored:
    @pytest.fixture
    def attempt(self, stored: dict[str, str], user: User) -> Attempt:
        install()
        return Attempt.objects.create(
            user=user,
            problem=Problem.objects.get(slug=COINS.slug),
            language=Language.objects.get(code="py313"),
            source_code="x",
        )

    def test_a_partial_score_is_kept_and_is_not_a_solve(self, attempt: Attempt, user: User) -> None:
        apply_result({"attempt_id": attempt.pk, "verdict": "PARTIAL", "score": 70})
        attempt.refresh_from_db()
        assert (attempt.verdict, attempt.score) == ("PARTIAL", 70)
        assert not UserSolvedProblem.objects.filter(user=user, problem=attempt.problem).exists()

    def test_the_full_score_is_a_solve(self, attempt: Attempt, user: User) -> None:
        apply_result({"attempt_id": attempt.pk, "verdict": "AC", "score": 100})
        assert UserSolvedProblem.objects.filter(user=user, problem=attempt.problem).exists()

    def test_the_api_returns_the_score(self, attempt: Attempt, user: User) -> None:
        apply_result({"attempt_id": attempt.pk, "verdict": "PARTIAL", "score": 25})
        client = APIClient()
        client.force_authenticate(user)
        body = client.get(reverse("attempt-detail", args=[attempt.pk])).json()
        assert (body["verdict"], body["score"]) == ("PARTIAL", 25)
        row = client.get(reverse("attempt-list"), {"problem": COINS.slug}).json()["results"][0]
        assert (row["verdict"], row["score"]) == ("PARTIAL", 25)

    def test_an_interactive_attempt_reports_no_test_total(
        self, stored: dict[str, str], user: User
    ) -> None:
        """One dialogue is judged, not the tests: "0 of 3 passed" on an
        accepted attempt would be a lie."""
        install()
        attempt = Attempt.objects.create(
            user=user,
            problem=Problem.objects.get(slug=GUESS.slug),
            language=Language.objects.get(code="py313"),
            source_code="x",
        )
        apply_result({"attempt_id": attempt.pk, "verdict": "AC", "score": 100})
        client = APIClient()
        client.force_authenticate(user)
        assert client.get(reverse("attempt-detail", args=[attempt.pk])).json()["tests_total"] == 0


# ── task kind: function (ADR-0053) ───────────────────────────────────────────


class TestFunctionKind:
    def test_a_family_covers_every_version_of_a_language(self) -> None:
        assert taskkinds.family("cpp23") == "cpp"
        assert taskkinds.supports_function("pypy73")
        assert taskkinds.supports_function("csharp14")
        assert not taskkinds.supports_function("pascal322")

    def test_a_harness_needs_the_marker_once_on_its_own_line(self) -> None:
        marker = taskkinds.SOLUTION_MARKER
        assert taskkinds.harness_error(f"a\n{marker}\nb\n") is None
        assert taskkinds.harness_error("") is not None
        assert taskkinds.harness_error("int main() {}\n") is not None
        assert taskkinds.harness_error(f"{marker}\n{marker}\n") is not None
        assert taskkinds.harness_error(f"x = '{marker}'\n") is not None

    def test_the_submission_replaces_the_marker_line_and_is_not_expanded(self) -> None:
        marker = taskkinds.SOLUTION_MARKER
        program = taskkinds.compose(f"head\n{marker}\ntail\n", f"f()  # {marker}\n")
        assert program == f"head\nf()  # {marker}\ntail\n"

    @pytest.mark.parametrize(
        ("io_mode", "checker_type", "ok"),
        [
            ("stdio", "standard", True),
            ("stdio", "special", True),
            ("stdio", "scorer", True),
            ("stdio", "interactive", False),
            ("both", "standard", False),
        ],
    )
    def test_what_a_function_problem_can_be_combined_with(
        self, io_mode: str, checker_type: str, ok: bool
    ) -> None:
        assert (task_kind_error("function", io_mode, checker_type) is None) is ok
        assert task_kind_error("program", io_mode, checker_type) is None

    def test_the_staff_api_refuses_an_interactive_function_problem(
        self, staff_client: APIClient, problem: Problem, python: Language
    ) -> None:
        Problem.objects.filter(pk=problem.pk).update(
            checker_type="interactive", interactor_source="x", interactor_language=python
        )
        response = staff_client.patch(
            reverse("staff-problem-detail", args=[problem.slug]),
            {"task_kind": "function"},
            format="json",
        )
        assert response.status_code == 400, response.content
        assert EVALUATION_MODE_INVALID in json.dumps(response.json())

    def test_the_model_refuses_a_function_problem_with_file_io(self, problem: Problem) -> None:
        problem.task_kind, problem.io_mode = "function", BOTH
        with pytest.raises(ValidationError):
            problem.clean()

    def test_a_function_problem_without_a_harness_cannot_be_released(
        self, problem: Problem, python: Language
    ) -> None:
        Problem.objects.filter(pk=problem.pk).update(task_kind="function")
        problem.refresh_from_db()
        assert "lists no languages" in (evaluation_error(problem) or "")
        row = ProblemLanguage.objects.create(problem=problem, language=python)
        assert "harness is empty" in (evaluation_error(problem) or "")
        row.harness = f"{taskkinds.SOLUTION_MARKER}\nmain()\n"
        row.save()
        assert evaluation_error(problem) is None
        assert release.evaluation_gate(problem).passed
        pascal, _ = Language.objects.get_or_create(
            code="pascal322", defaults={"name": "Pascal", "run_cmd": ["x"]}
        )
        ProblemLanguage.objects.create(problem=problem, language=pascal, harness=row.harness)
        assert "not offered" in (evaluation_error(problem) or "")

    def test_the_reference_problem_is_open_in_eleven_languages(
        self, stored: dict[str, str]
    ) -> None:
        install()
        problem = Problem.objects.get(slug=MAXPAIR.slug)
        assert problem.languages.count() == len(MAXPAIR.languages) == 11
        body = APIClient().get(reverse("problem-detail", args=[problem.slug])).json()
        assert body["task_kind"] == "function"
        by_code = {row["code"]: row for row in body["languages"]}
        assert set(by_code) == {lang.code for lang in MAXPAIR.languages}
        for lang in MAXPAIR.languages:
            assert by_code[lang.code]["harness"] == lang.harness
            assert by_code[lang.code]["code_template"] == lang.stub
            assert taskkinds.harness_error(lang.harness) is None

    def test_the_job_carries_the_composed_program(self, stored: dict[str, str], user: User) -> None:
        install()
        problem = Problem.objects.get(slug=MAXPAIR.slug)
        for lang in MAXPAIR.languages:
            attempt = Attempt.objects.create(
                user=user,
                problem=problem,
                language=Language.objects.get(code=lang.code),
                source_code=lang.solution,
            )
            source = json.loads(build_job(attempt).to_json())["source"]
            assert lang.solution.strip() in source
            assert taskkinds.SOLUTION_MARKER not in source
            assert source == taskkinds.compose(lang.harness, lang.solution)
            # What the solver sent is what is stored - not the composed program.
            assert attempt.source_code == lang.solution

    def test_a_language_without_a_harness_is_refused_at_submission(
        self, stored: dict[str, str], user: User
    ) -> None:
        install()
        Language.objects.get_or_create(
            code="lua54", defaults={"name": "Lua", "run_cmd": ["lua", "{src}"]}
        )
        client = APIClient()
        client.force_authenticate(user)
        response = client.post(
            reverse("attempt-list"),
            {"problem": MAXPAIR.slug, "language": "lua54", "source_code": "x"},
            format="json",
        )
        assert response.status_code == 400, response.content
        assert "language" in json.dumps(response.json())

    def test_each_python_submission_earns_its_listed_verdict(
        self, stored: dict[str, str], tmp_path: Path
    ) -> None:
        """The harness and the submission, joined and actually run."""
        harness = next(lang.harness for lang in MAXPAIR.languages if lang.code == "py313")
        ran = 0
        for case in MAXPAIR.cases:
            if (case.language or "py313") != "py313":
                continue
            program = taskkinds.compose(harness, case.source)
            passed = all(
                _run(program, test_in, tmp_path).stdout.split() == expected.split()
                for test_in, expected, _group in MAXPAIR.tests
            )
            assert ("AC" if passed else "WA") == case.verdict, case.name
            ran += 1
        assert ran == 3
