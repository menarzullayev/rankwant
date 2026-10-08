package main

import (
	"context"
	"testing"
)

func TestAnswerTestVerdict(t *testing.T) {
	for points, want := range map[int]string{100: VAC, 250: VAC, 99: VPartial, 1: VPartial, 0: VWA} {
		if got := answerTestVerdict(points); got != want {
			t.Errorf("%d points: %s, want %s", points, got, want)
		}
	}
}

// Every file is graded on its own: a wrong one does not stop the rest, a
// missing one scores zero without the checker being asked.
func TestGradeAnswers(t *testing.T) {
	work := t.TempDir()
	// The score is whatever the answer file says; an empty file would make
	// the checker fail, which is how a call for a missing answer would show.
	cmd := writeScript(t, work, `cat "$2"`)

	job := &Job{
		Checker: Checker{Type: "scorer"},
		Tests: []Test{
			{Index: 1, Input: "a", Expected: "x", Answer: "100"},
			{Index: 2, Input: "b", Expected: "x", Answer: "0"},
			{Index: 3, Input: "c", Expected: "x"},
			{Index: 4, Input: "d", Expected: "x", Answer: "60"},
		},
	}
	res := &Result{PerTest: []TestResult{}}
	gradeAnswers(context.Background(), work, cmd, job, nil, nil, res)

	if res.Verdict != VPartial || res.Score != 40 {
		t.Fatalf("got %s/%d, want PARTIAL/40", res.Verdict, res.Score)
	}
	want := []string{VAC, VWA, VWA, VPartial}
	if len(res.PerTest) != len(want) {
		t.Fatalf("%d tests graded, want %d", len(res.PerTest), len(want))
	}
	for i, v := range want {
		if res.PerTest[i].Verdict != v {
			t.Errorf("test %d: %s, want %s", i+1, res.PerTest[i].Verdict, v)
		}
	}
	if res.FailedTestIndex == nil || *res.FailedTestIndex != 2 {
		t.Errorf("first failing test: %v, want 2", res.FailedTestIndex)
	}
}

func TestGradeAnswersAllRight(t *testing.T) {
	work := t.TempDir()
	cmd := writeScript(t, work, `cat "$2"`)
	job := &Job{
		Checker: Checker{Type: "scorer"},
		Tests:   []Test{{Index: 1, Input: "a", Answer: "100"}, {Index: 2, Input: "b", Answer: "100"}},
	}
	res := &Result{PerTest: []TestResult{}}
	gradeAnswers(context.Background(), work, cmd, job, nil, nil, res)
	if res.Verdict != VAC || res.Score != 100 || res.FailedTestIndex != nil {
		t.Fatalf("got %s/%d (failed %v), want AC/100", res.Verdict, res.Score, res.FailedTestIndex)
	}
}

// A checker that breaks is the author's fault and must not become a zero.
func TestGradeAnswersCheckerFailure(t *testing.T) {
	work := t.TempDir()
	cmd := writeScript(t, work, `echo "no number"`)
	job := &Job{Checker: Checker{Type: "scorer"}, Tests: []Test{{Index: 1, Input: "a", Answer: "x"}}}
	res := &Result{PerTest: []TestResult{}}
	gradeAnswers(context.Background(), work, cmd, job, nil, nil, res)
	if res.Verdict != VCheckerErr {
		t.Fatalf("got %s, want %s", res.Verdict, VCheckerErr)
	}
}

func TestAnswerTaskNeedsAChecker(t *testing.T) {
	res := &Result{PerTest: []TestResult{}}
	judgeAnswers(context.Background(), t.TempDir(), &Job{Checker: Checker{Type: "standard"}}, nil, nil, res)
	if res.Verdict != VIE {
		t.Fatalf("got %s, want IE", res.Verdict)
	}
}
