"""Content readiness — the state machine and the semantic gate (D8 · ADR-0037).

`readiness` answers "is this problem's CONTENT trustworthy?". That is a
different question from `is_public`, which answers "can it be seen?". D8-F
keeps the archive public while locking it out of graded contests, so the two
flags must never be derived from one another: 1 222 archive problems have no
hidden test and would become private if visibility were tied to readiness.

The criterion is semantic, not numeric. An arbitrary threshold such as "at
least five hidden tests" was explicitly rejected (D8): the number a problem
needs depends on its type — one hidden test may be enough for an interactive
problem. Four conditions decide whether a problem may reach `validated`:

  S1 a hidden test EXISTS (`tests.filter(is_sample=False).exists()`)
  S2 the checker type is complete (program + language when one is required)
  S3 the reference solution is AC on every test (judge harness)
  S4 a program that prints the sample is NOT AC (judge harness)

S1 and S2 are static and evaluated here. S3 and S4 need a judge and are
evaluated by `run_harness()` through the same provider the submit flow uses,
so tests can replace the judge without touching this module.

[ADR-0037]: ../../../docs/07-adr/0037-content-integrity-gate.md
"""

from __future__ import annotations

import json
import logging
from typing import Any

from django.core.exceptions import ValidationError

from judging.provider import get_provider
from judging.services import build_standalone_job
from judging.verdicts import Verdict
from problems.models import Language, Problem, ReferenceSolution

log = logging.getLogger(__name__)

Readiness = Problem.Readiness

#: The only readiness allowed into a graded contest (D8-F).
GRADED_READY = Readiness.VALIDATED

#: One forward step at a time. A jump such as `draft -> validated` is not in
#: this map and is therefore rejected (R10).
FORWARD: dict[str, str] = {
    Readiness.DRAFT: Readiness.NEEDS_TESTS,
    Readiness.NEEDS_TESTS: Readiness.HAS_HIDDEN_TESTS,
    Readiness.HAS_HIDDEN_TESTS: Readiness.CHECKER_VALIDATED,
    Readiness.CHECKER_VALIDATED: Readiness.REF_SOLUTION_VERIFIED,
    Readiness.REF_SOLUTION_VERIFIED: Readiness.VALIDATED,
}

_ALWAYS = frozenset({Readiness.BLOCKED, Readiness.NEEDS_REVIEW})

#: Allowed transitions. `blocked` is reachable from any state because the
#: harness may discover a broken problem at any point; `needs_review` is the
#: way back — `blocked` and `legacy_unverified` never reach `validated`
#: directly, they go through the chain again.
ALLOWED: dict[str, frozenset[str]] = {
    Readiness.DRAFT: frozenset({Readiness.NEEDS_TESTS}) | _ALWAYS,
    Readiness.NEEDS_TESTS: frozenset({Readiness.HAS_HIDDEN_TESTS}) | _ALWAYS,
    Readiness.HAS_HIDDEN_TESTS: frozenset({Readiness.CHECKER_VALIDATED}) | _ALWAYS,
    Readiness.CHECKER_VALIDATED: frozenset({Readiness.REF_SOLUTION_VERIFIED}) | _ALWAYS,
    Readiness.REF_SOLUTION_VERIFIED: frozenset({Readiness.VALIDATED}) | _ALWAYS,
    Readiness.VALIDATED: _ALWAYS,
    Readiness.LEGACY_UNVERIFIED: _ALWAYS,
    Readiness.BLOCKED: frozenset({Readiness.NEEDS_REVIEW}),
    Readiness.NEEDS_REVIEW: frozenset({Readiness.CHECKER_VALIDATED, Readiness.BLOCKED}),
}


class HarnessError(RuntimeError):
    """The judge did not answer a readiness probe.

    Distinct from a `blocked` result: no answer is an infrastructure problem,
    not evidence that the problem is broken. Silently writing `blocked` here
    would lock every problem out of contests during a judge outage.
    """


def has_hidden_test(problem: Problem) -> bool:
    """S1 — a hidden test exists.

    Existence, never a count: "at least five" would be an arbitrary number
    (D8) and would fail interactive problems that need a single one.
    """
    return problem.tests.filter(is_sample=False).exists()


def checker_ready(problem: Problem) -> bool:
    """S2 — the configured checker type is complete.

    `standard` needs nothing. `special`/`scorer` need a checker program and
    its language; `interactive` needs an interactor and its language. Without
    them every submission returns IE, so the problem cannot be graded at all.
    """
    kind = problem.checker_type
    if kind == Problem.Checker.STANDARD:
        return True
    if kind == Problem.Checker.INTERACTIVE:
        source, language_id = problem.interactor_source, problem.interactor_language_id
    else:
        # `special` and `scorer` — the judge waits for a checker program.
        source, language_id = problem.checker_source, problem.checker_language_id
    return bool(source.strip()) and language_id is not None


def reference_solution(problem: Problem) -> ReferenceSolution | None:
    """The reference solution row, or `None`.

    Queried, not touched through the OneToOne accessor: `problem.reference_solution`
    raises `RelatedObjectDoesNotExist` when it is missing.
    """
    return ReferenceSolution.objects.filter(problem=problem).first()


def requirement_error(problem: Problem, target: str) -> str | None:
    """The unmet semantic condition for `target`, or `None` when it is met.

    Entering `has_hidden_tests` and beyond requires S1; `checker_validated`
    and beyond require S2; `ref_solution_verified` and beyond require a
    reference solution to exist (that it is actually AC — S3 — is proven by
    the harness, which is the only thing that moves a problem into
    `ref_solution_verified`).
    """
    needs_tests = {
        Readiness.HAS_HIDDEN_TESTS,
        Readiness.CHECKER_VALIDATED,
        Readiness.REF_SOLUTION_VERIFIED,
        Readiness.VALIDATED,
    }
    needs_checker = {
        Readiness.CHECKER_VALIDATED,
        Readiness.REF_SOLUTION_VERIFIED,
        Readiness.VALIDATED,
    }
    needs_reference = {Readiness.REF_SOLUTION_VERIFIED, Readiness.VALIDATED}
    if target in needs_tests and not has_hidden_test(problem):
        return "S1: the problem needs at least one hidden (non-sample) test"
    if target in needs_checker:
        # S2 is "this problem can be graded at all": a complete checker is
        # one half, a pair of modes the judge implements is the other.
        from problems.evaluation import evaluation_error

        invalid = evaluation_error(problem)
        if invalid:
            return f"S2: {invalid}"
    if target in needs_checker and not checker_ready(problem):
        return (
            f"S2: checker type '{problem.checker_type}' is incomplete — "
            "a checker program and its language are required"
        )
    if target in needs_reference and reference_solution(problem) is None:
        return "S3: the problem has no reference solution"
    return None


def enforcing() -> bool:
    """Is the staged rollout finished? (ADR 0050)

    The rules below are the spec and the acceptance tests expect them to
    reject. Production cannot take the rejection yet: the live database has
    **no** problem in `GRADED_READY`, so enforcing would refuse every problem
    attachment to a contest. Until the content is promoted it runs with
    `READINESS_ENFORCE=0` and the gates report instead of blocking.
    """
    from django.conf import settings

    return bool(getattr(settings, "READINESS_ENFORCE", True))


def gate(message: str) -> None:
    """Enforce the rule, or report it while the rollout is on (ADR 0050)."""
    if enforcing():
        raise ValidationError({"readiness": message})
    log.warning("readiness gate NOT enforced (READINESS_ENFORCE=0): %s", message)


def assert_transition(current: str, target: str) -> None:
    """Reject a jump the state machine does not allow (R10)."""
    if current == target:
        return
    allowed = ALLOWED.get(current, frozenset())
    if target not in allowed:
        gate(
            f"'{current}' -> '{target}' is not allowed: readiness moves one step "
            f"at a time ({', '.join(sorted(allowed)) or 'no transition'})"
        )


def graded_gate_error(problem: Problem) -> str | None:
    """D8-F — `None` when the problem may enter a graded contest.

    Every contest is graded (standings are computed for it), so the gate sits
    where the problem is attached, not in the submit flow.
    """
    if problem.readiness == GRADED_READY:
        return None
    return (
        f"problem '{problem.slug}' cannot enter a graded contest: readiness is "
        f"'{problem.readiness}', only '{GRADED_READY}' is accepted"
    )


def evaluate_readiness(
    problem: Problem,
    *,
    ref_verdict: str,
    echo_verdict: str,
    previous: str,
) -> str:
    """The readiness implied by two judge verdicts — no judge needed here.

    Pure function, so the semantic gate is testable without a sandbox: it is
    the only place that turns S3/S4 evidence into a state.

    `ref_verdict` — verdict of the reference solution (S3).
    `echo_verdict` — verdict of the program that prints the sample (S4).
    """
    if not has_hidden_test(problem):  # S1
        return previous
    if not checker_ready(problem):  # S2
        return previous
    if echo_verdict == Verdict.AC:  # S4
        return Readiness.BLOCKED
    if ref_verdict != Verdict.AC:  # S3
        return Readiness.BLOCKED
    return Readiness.REF_SOLUTION_VERIFIED


#: A program that prints one fixed string — the sample answer — whatever the
#: input is. That is exactly the `print('3 2 1')` shortcut S4 exists to kill.
#: Keyed by `Language.code`; a missing code fails loudly (see
#: `sample_echo_source`) instead of silently judging nothing.
ECHO_TEMPLATES: dict[str, str] = {
    "cpp23": "#include <bits/stdc++.h>\nint main() {{ std::cout << {payload}; }}\n",
    "py313": 'print({payload}, end="")\n',
    "java21": "public class Main {{ public static void main(String[] a) {{"
    " System.out.print({payload}); }} }}\n",
    "go124": 'package main\n\nimport "fmt"\n\nfunc main() {{ fmt.Print({payload}) }}\n',
    "php84": "<?php echo {payload};\n",
    "php": "<?php echo {payload};\n",
}


def _string_literal(payload: str, code: str) -> str:
    """`payload` as a source-level string literal for this language."""
    if code.startswith("py"):
        return repr(payload)
    # C, C++, Java, Go and PHP all accept JSON escaping. `ensure_ascii=False`
    # keeps UTF-8 text readable — `\\uXXXX` is not a C escape.
    return json.dumps(payload, ensure_ascii=False)


def sample_echo_source(problem: Problem, language: Language) -> str:
    """S4 — source of the program that prints the sample answer.

    The sample test is taken first: it is the answer published on the problem
    page, i.e. the one a cheater would copy. A problem with no sample falls
    back to its first test.
    """
    test = (
        problem.tests.filter(is_sample=True).order_by("order").first()
        or problem.tests.order_by("order").first()
    )
    if test is None:
        raise HarnessError(f"'{problem.slug}' has no test to echo")
    template = ECHO_TEMPLATES.get(language.code)
    if template is None:
        raise HarnessError(
            f"no sample-echo template for language '{language.code}' — "
            f"add one to problems.readiness.ECHO_TEMPLATES"
        )
    from problems.storage import get_test_data

    payload = get_test_data(test.output_ref)
    return template.format(payload=_string_literal(payload, language.code))


def _submit_and_wait(
    provider: Any,
    problem: Problem,
    language: Language,
    source: str,
    *,
    poll_timeout: int,
    rounds: int,
) -> str:
    """Submits one standalone job and returns its verdict."""
    job = build_standalone_job(problem, source, language)
    provider.submit(job)
    for _ in range(max(1, rounds)):
        result = provider.poll(timeout=poll_timeout)
        if result is None:
            continue
        if result.get("job_id") == job.job_id:
            return str(result.get("verdict") or Verdict.IE)
        log.warning(
            "readiness: result for another job arrived (%s, expected %s)",
            result.get("job_id"),
            job.job_id,
        )
    raise HarnessError(
        f"the judge did not answer job {job.job_id} for '{problem.slug}' in {rounds} poll(s)"
    )


def run_harness(
    problem: Problem,
    *,
    provider: Any = None,
    language: Language | None = None,
    ref_source: str | None = None,
    echo_source: str | None = None,
    poll_timeout: int = 1,
    rounds: int = 2,
) -> tuple[str, str]:
    """Runs S3 and S4 through the judge — returns `(ref_verdict, echo_verdict)`.

    No `Attempt` is created: a readiness probe is not a submission and must
    not move attempt counters, standings or ratings. The job is standalone
    (`attempt_id=0`) exactly like `enqueue_custom`.

    ⚠️ Against the real Redis queue a running `beat` would swallow the result
    (`drain_results` routes `attempt_id=0` with no `hack_id`/`custom_run_id`
    to `apply_result`, which drops it). Run the real-judge mode with `beat`
    stopped — CI/nightly — as the bake-off discipline requires.
    """
    row = reference_solution(problem)
    if row is None:
        raise HarnessError(f"'{problem.slug}' has no reference solution")
    lang = language if language is not None else row.language
    ref = row.source if ref_source is None else ref_source
    echo = sample_echo_source(problem, lang) if echo_source is None else echo_source
    queue = provider if provider is not None else get_provider()
    ref_verdict = _submit_and_wait(
        queue, problem, lang, ref, poll_timeout=poll_timeout, rounds=rounds
    )
    echo_verdict = _submit_and_wait(
        queue, problem, lang, echo, poll_timeout=poll_timeout, rounds=rounds
    )
    if ref_verdict == Verdict.IE or echo_verdict == Verdict.IE:
        raise HarnessError(
            f"'{problem.slug}': the judge returned IE (ref={ref_verdict}, "
            f"echo={echo_verdict}) — infrastructure, not a verdict"
        )
    return ref_verdict, echo_verdict


def verify(
    problem: Problem,
    *,
    provider: Any = None,
    ref_source: str | None = None,
    echo_source: str | None = None,
) -> str:
    """The readiness the harness proves — computed, not written.

    `blocked` is written on broken evidence; a healthy problem only reaches
    `ref_solution_verified` here — `validated` needs the staff signature.
    """
    previous = problem.readiness
    ref_verdict, echo_verdict = run_harness(
        problem, provider=provider, ref_source=ref_source, echo_source=echo_source
    )
    target = evaluate_readiness(
        problem, ref_verdict=ref_verdict, echo_verdict=echo_verdict, previous=previous
    )
    if target != previous:
        assert_transition(previous, target)
    return target


def apply_verdict(problem: Problem, target: str) -> str:
    """Writes a harness result, refusing a jump the machine does not allow."""
    if target == problem.readiness:
        return target
    assert_transition(problem.readiness, target)
    problem.readiness = target
    problem.save(update_fields=["readiness"])
    return target
