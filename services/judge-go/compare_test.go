package main

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestExactComparisonIsUnchanged(t *testing.T) {
	cases := []struct{ got, want, verdict string }{
		{"3\n", "3", VAC},
		{"3  \n\n", "3\n", VAC},
		{"1\n2\n", "1 2\n", VPE},
		{"2.0\n", "2\n", VWA},
	}
	for _, c := range cases {
		if v := compareAnswer(c.got, c.want, Compare{}); v != c.verdict {
			t.Errorf("exact %q vs %q = %s, want %s", c.got, c.want, v, c.verdict)
		}
	}
}

func TestRealComparisonTolerance(t *testing.T) {
	cmp := Compare{Epsilon: 1e-6}
	cases := []struct{ got, want, verdict string }{
		// The same number written differently.
		{"2.000000\n", "2\n", VAC},
		{"1e-07\n", "0.0000001\n", VAC},
		{".5\n", "0.5\n", VAC},
		{"3.\n", "3\n", VAC},
		// Absolute below one, relative above it.
		{"1.0000005\n", "1\n", VAC},
		{"1.000002\n", "1\n", VWA},
		{"1000000.5\n", "1000000\n", VAC},
		{"1000002\n", "1000000\n", VWA},
		{"-0.0000004\n", "0\n", VAC},
		// Layout is not the question: no PE.
		{"1\n2\n", "1.0 2.0\n", VAC},
		// Token count and order.
		{"1 2 3\n", "1 2\n", VWA},
		{"2 1\n", "1 2\n", VWA},
		{"", "1\n", VWA},
		// Non-numbers where the jury has a number.
		{"nan\n", "1\n", VWA},
		{"inf\n", "1e400\n", VWA},
		{"0x1p0\n", "1\n", VWA},
		{"1_0\n", "10\n", VWA},
		{"1,5\n", "1.5\n", VWA},
		// Words in the jury's answer are compared as text.
		{"YES 1.50000\n", "YES 1.5\n", VAC},
		{"yes 1.5\n", "YES 1.5\n", VWA},
	}
	for _, c := range cases {
		if v := compareAnswer(c.got, c.want, cmp); v != c.verdict {
			t.Errorf("real %q vs %q = %s, want %s", c.got, c.want, v, c.verdict)
		}
	}
}

func TestRealComparisonUsesTheJobTolerance(t *testing.T) {
	loose := &Job{Checker: Checker{Type: CheckerReal, Epsilon: 1e-3}}
	if v := compareAnswer("1.0004\n", "1\n", compareFor(loose)); v != VAC {
		t.Fatalf("1e-3 tolerance: %s", v)
	}
	plain := &Job{Checker: Checker{Type: CheckerReal}}
	if got := compareFor(plain).Epsilon; got != DefaultEpsilon {
		t.Fatalf("missing epsilon = %g, want %g", got, DefaultEpsilon)
	}
	if got := compareFor(&Job{Checker: Checker{Type: CheckerStandard}}); got != (Compare{}) {
		t.Fatalf("standard job compares with %+v", got)
	}
}

// In file mode the same rule reads output.txt (the 33 File and Text
// problems of the Abramyan book that have real answers).
func TestRealComparisonReadsOutputFile(t *testing.T) {
	work := t.TempDir()
	if err := os.WriteFile(filepath.Join(work, "output.txt"), []byte("2.500000\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	out := &runOutcome{ExitCode: 0}
	test := Test{Index: 1, Expected: "2.5\n"}
	lim := Limits{TimeMS: 1000, MemoryKB: 65536}
	if v := classifyAnswer(out, test, lim, work, IO{Mode: "both"}, Compare{Epsilon: 1e-6}); v != VAC {
		t.Fatalf("output.txt with a real answer = %s, want AC", v)
	}
	if v := classifyAnswer(out, test, lim, work, IO{Mode: "both"}, Compare{}); v != VWA {
		t.Fatalf("the same file compared exactly = %s, want WA", v)
	}
}

// Before ADR-0060 an unknown type fell through to the exact comparison.
func TestUnknownCheckerIsRefused(t *testing.T) {
	job := &Job{JobID: "j", Checker: Checker{Type: "fuzzy"}, Tests: []Test{{Index: 1}}}
	res := judge(context.Background(), job, nil, nil)
	if res.Verdict != VIE || !strings.Contains(res.CompileOutput, "unsupported checker type") {
		t.Fatalf("verdict %s, reason %q", res.Verdict, res.CompileOutput)
	}
	for _, kind := range []string{"", CheckerStandard, CheckerSpecial, CheckerInteractive, CheckerScorer, CheckerReal} {
		if !knownChecker(kind) {
			t.Fatalf("%q must be known", kind)
		}
	}
}
