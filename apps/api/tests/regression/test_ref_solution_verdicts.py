"""R6 · R7 — the two judge verdicts that decide readiness (D8 · ADR-0037).

The bug this file exists for was measured on `3-ta-son`: the expected answer
was published on the problem page, so `print('3 2 1')` was accepted. The
product's core — "solving means solving" — rests on those four lines.

  R6  the reference solution is AC                 -> `ref_solution_verified`
  R7  printing the sample is also AC              -> `blocked`

Note what is NOT here: a count of hidden tests. D8 forbids an arbitrary
number; a single hidden test is enough as long as copying the sample loses.
"""

from __future__ import annotations

import pytest

from judging.verdicts import Verdict
from problems.models import Problem
from problems.readiness import apply_verdict, verify


@pytest.mark.django_db
class TestReferenceSolutionVerdicts:
    def test_reference_solution_is_ac(self, ready_problem, scripted_judge) -> None:
        """R6 — S3 holds and S4 holds, so the harness advances the problem."""
        scripted_judge({"ref": Verdict.AC, "echo": Verdict.WA})
        target = verify(ready_problem, ref_source="ref", echo_source="echo")
        assert target == Problem.Readiness.REF_SOLUTION_VERIFIED

        apply_verdict(ready_problem, target)
        ready_problem.refresh_from_db()
        assert ready_problem.readiness == Problem.Readiness.REF_SOLUTION_VERIFIED

    def test_sample_echo_is_not_ac(self, ready_problem, scripted_judge) -> None:
        """R7 — the sample echoer is accepted, so the problem is broken."""
        scripted_judge({"ref": Verdict.AC, "echo": Verdict.AC})
        target = verify(ready_problem, ref_source="ref", echo_source="echo")
        assert target == Problem.Readiness.BLOCKED

        apply_verdict(ready_problem, target)
        ready_problem.refresh_from_db()
        assert ready_problem.readiness == Problem.Readiness.BLOCKED

    def test_reference_solution_not_ac_blocks(self, ready_problem, scripted_judge) -> None:
        """S3 — a reference solution that does not pass is broken content."""
        scripted_judge({"ref": Verdict.WA, "echo": Verdict.WA})
        target = verify(ready_problem, ref_source="ref", echo_source="echo")
        assert target == Problem.Readiness.BLOCKED

    def test_blocked_problem_can_return_to_review(self, ready_problem, scripted_judge) -> None:
        """`blocked` is not terminal — staff fixes it and asks for a review."""
        scripted_judge({"ref": Verdict.AC, "echo": Verdict.AC})
        apply_verdict(ready_problem, verify(ready_problem, ref_source="ref", echo_source="echo"))
        ready_problem.readiness = Problem.Readiness.NEEDS_REVIEW
        ready_problem.full_clean()
        ready_problem.save(update_fields=["readiness"])
        assert ready_problem.readiness == Problem.Readiness.NEEDS_REVIEW

    def test_no_hidden_test_keeps_the_state(self, problem, language, scripted_judge) -> None:
        """S1 — without a hidden test the harness must not promote anything."""
        from problems.models import ReferenceSolution

        ReferenceSolution.objects.create(problem=problem, language=language, source="ref")
        scripted_judge({"ref": Verdict.AC, "echo": Verdict.WA})
        # `problem` has one test and it is not a sample — remove that edge and
        # the probe has nothing to prove.
        problem.tests.update(is_sample=True)
        assert verify(problem, ref_source="ref", echo_source="echo") == problem.readiness
