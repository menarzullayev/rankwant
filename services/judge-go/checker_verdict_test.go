package main

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"testing"
)

// A checker sees PE as well as AC and WA; it never sees a resource verdict.
func TestCheckerDecides(t *testing.T) {
	for _, v := range []string{VAC, VWA, VPE} {
		if !checkerDecides(v) {
			t.Errorf("%s must go to the checker", v)
		}
	}
	for _, v := range []string{VTLE, VMLE, VOLE, VRE, VRESignal, VIdle, VIE} {
		if checkerDecides(v) {
			t.Errorf("%s must not go to the checker", v)
		}
	}
}

// AC is the full score; a positive score below it is PARTIAL, not "solved".
func TestScorerVerdict(t *testing.T) {
	cases := []struct {
		worst string
		score int
		want  string
	}{
		{VAC, 100, VAC},
		{VAC, 99, VPartial},
		{VAC, 1, VPartial},
		{VAC, 0, VWA},
		{VTLE, 40, VTLE}, // the caller turns a failed run with points into PARTIAL
		{VIE, 0, VIE},
	}
	for _, c := range cases {
		if got := scorerVerdict(c.worst, c.score); got != c.want {
			t.Errorf("scorerVerdict(%s, %d) = %s, want %s", c.worst, c.score, got, c.want)
		}
	}
}

// writeScript puts a shell checker into the work directory.
func writeScript(t *testing.T, dir, body string) []string {
	t.Helper()
	path := filepath.Join(dir, "checker.sh")
	if err := os.WriteFile(path, []byte("#!/bin/sh\n"+body+"\n"), 0o755); err != nil {
		t.Fatal(err)
	}
	return []string{"/bin/sh", path}
}

// The checker is called as `checker <input> <output> <answer>` and its
// exit code decides a `special` problem.
func TestRunCheckerSpecial(t *testing.T) {
	work := t.TempDir()
	// Accepts when the contestant's output equals the INPUT reversed: a rule
	// no comparison with the jury's answer could express.
	cmd := writeScript(t, work, `[ "$(rev "$1")" = "$(cat "$2")" ]`)

	good, err := runChecker(context.Background(), work, cmd, "special", "abc", "cba", "ignored")
	if err != nil || good.Verdict != VAC || good.Score != 100 {
		t.Fatalf("accepted answer: %+v, %v", good, err)
	}
	bad, err := runChecker(context.Background(), work, cmd, "special", "abc", "abc", "ignored")
	if err != nil || bad.Verdict != VWA {
		t.Fatalf("rejected answer: %+v, %v", bad, err)
	}
}

// A scorer's last line is the score: 0 is WA, above 100 is capped, and a
// checker that prints no number is the author's error, not the solver's.
func TestRunCheckerScorer(t *testing.T) {
	work := t.TempDir()
	cmd := writeScript(t, work, `cat "$2"`) // the score is whatever the contestant printed

	cases := []struct {
		output  string
		verdict string
		score   int
	}{
		{"100", VAC, 100},
		{"37", VAC, 37},
		{"note\n64", VAC, 64},
		{"0", VWA, 0},
		{"250", VAC, 100},
		{"no number here", VCheckerErr, 0},
	}
	for _, c := range cases {
		got, err := runChecker(context.Background(), work, cmd, "scorer", "in", c.output, "ans")
		if err != nil || got.Verdict != c.verdict || got.Score != c.score {
			t.Errorf("output %q: %+v (%v), want %s/%d", c.output, got, err, c.verdict, c.score)
		}
	}
}

// Who stopped first decides the blame in an interactive run.
func TestInteractiveVerdict(t *testing.T) {
	exit1 := errors.New("exit status 1")
	killed := errors.New("signal: killed")
	cases := []struct {
		name            string
		timedOut        bool
		cpu, limit      int64
		subErr, itErr   error
		interactorFirst bool
		want            string
	}{
		{"accepted", false, 20, 1000, nil, nil, false, VAC},
		{"wrong final answer", false, 20, 1000, nil, exit1, false, VWA},
		// The interactor rejected and left; what became of the solution
		// afterwards - it ran to the end, or the judge stopped it - does
		// not change that. A wrong answer, not a crash and not a hang.
		{"rejected, solution ran on", false, 20, 1000, nil, exit1, true, VWA},
		{"rejected, solution stopped by the judge", false, 20, 1000, killed, exit1, true, VWA},
		// The solution crashed first; the interactor only saw the end of input.
		{"solution crashed first", false, 20, 1000, exit1, exit1, false, VRE},
		{"never flushed: both wait", true, 5, 1000, killed, killed, false, VIdle},
		{"busy loop", true, 3000, 1000, killed, killed, false, VTLE},
		{"too much CPU, finished", false, 1500, 1000, nil, nil, false, VTLE},
	}
	for _, c := range cases {
		got := interactiveVerdict(c.timedOut, c.cpu, c.limit, c.subErr, c.itErr, c.interactorFirst)
		if got != c.want {
			t.Errorf("%s: got %s, want %s", c.name, got, c.want)
		}
	}
}
