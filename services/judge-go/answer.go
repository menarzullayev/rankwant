package main

import (
	"context"
	"log/slog"
)

// Task kind "answer" (ADR-0053): the solver submits the answers, not a
// program. Nothing of the solver's is compiled or run, so there is no
// sandbox, no time and no memory to measure — only the checker, once per
// test, over the file that was submitted for it.
//
// The score is the mean of the per-test scores, as for a scorer problem:
// a `special` checker gives 100 or 0, a `scorer` whatever it prints. A
// test with no file scores 0 and is not shown to the checker — an empty
// answer and a missing one must not be told apart by the checker's mood.

// resolveAnswer returns the answer submitted for a test. `given` is false
// when the job carries neither the text nor a reference to it.
func resolveAnswer(ctx context.Context, test *Test, tests *store) (answer string, given bool, err error) {
	if test.Answer != "" {
		return test.Answer, true, nil
	}
	if test.AnswerRef == "" {
		return "", false, nil
	}
	data, err := tests.get(ctx, test.AnswerRef)
	if err != nil {
		return "", false, err
	}
	return string(data), true, nil
}

// answerTestVerdict — what one test of an answer task is shown as.
func answerTestVerdict(points int) string {
	switch {
	case points >= 100:
		return VAC
	case points > 0:
		return VPartial
	default:
		return VWA
	}
}

// gradeAnswers runs the prepared checker over every test and fills the
// result. Unlike the program path it never stops at the first failure:
// each file is an independent answer.
func gradeAnswers(ctx context.Context, work string, checkerCmd []string, job *Job,
	tests *store, emit Emit, res *Result) {

	sum := 0
	for _, test := range job.Tests {
		emitProgress(emit, job.AttemptID, test.Index)
		if err := resolve(ctx, &test, tests); err != nil {
			slog.Error("test ma'lumotini olish", "job", job.JobID, "test", test.Index, "err", err)
			res.Verdict = VIE
			return
		}
		answer, given, err := resolveAnswer(ctx, &test, tests)
		if err != nil {
			slog.Error("javob faylini olish", "job", job.JobID, "test", test.Index, "err", err)
			res.Verdict = VIE
			return
		}

		points := 0
		if given {
			cv, err := runChecker(ctx, work, checkerCmd, job.Checker.Type,
				test.Input, answer, test.Expected)
			if err != nil {
				res.Verdict = VIE
				return
			}
			if cv.Verdict == VCheckerErr {
				// The author's program failed: not the solver's fault,
				// and not a score of zero either.
				res.Verdict = VCheckerErr
				idx := test.Index
				res.FailedTestIndex = &idx
				return
			}
			points = cv.Score
		}
		sum += points

		tr := TestResult{Index: test.Index, Verdict: answerTestVerdict(points)}
		res.PerTest = append(res.PerTest, tr)
		emitTestFinished(emit, job.AttemptID, tr)
		if points < 100 && res.FailedTestIndex == nil {
			idx := test.Index
			res.FailedTestIndex = &idx
		}
	}
	res.Score = sum / len(job.Tests)
	res.Verdict = answerTestVerdict(res.Score)
}

// judgeAnswers — the whole of an answer job after the work directory exists.
func judgeAnswers(ctx context.Context, work string, job *Job, tests *store, emit Emit, res *Result) {
	if (job.Checker.Type != "special" && job.Checker.Type != "scorer") || job.Checker.Program == nil {
		// Comparing a hand-made file with the jury's byte for byte is not
		// what such a task means, and without a checker nothing can grade it.
		res.Verdict = VIE
		res.CompileOutput = "an answer task needs a special or scorer checker program"
		return
	}
	checkerCmd, err := prepareChecker(ctx, work, job.Checker.Program)
	if err != nil {
		res.Verdict = VCheckerErr
		res.CompileOutput = err.Error()
		return
	}
	gradeAnswers(ctx, work, checkerCmd, job, tests, emit, res)
}
