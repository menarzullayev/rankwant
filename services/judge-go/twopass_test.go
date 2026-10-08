package main

import (
	"context"
	"os"
	"path/filepath"
	"testing"
)

func TestCloneForRunLeavesTheAuthorsProgramsBehind(t *testing.T) {
	work := t.TempDir()
	for name, body := range map[string]string{
		"prog":             "binary",
		"main.py":          "source",
		"checker_main.py":  "secret",
		"manager.in":       "secret",
		"interactor_x.cpp": "secret",
	} {
		if err := os.WriteFile(filepath.Join(work, name), []byte(body), 0o755); err != nil {
			t.Fatal(err)
		}
	}
	if err := os.MkdirAll(filepath.Join(work, "pkg", "deep"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(work, "pkg", "deep", "a.class"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}

	dir, err := cloneForRun(work)
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(dir)

	for _, kept := range []string{"prog", "main.py", filepath.Join("pkg", "deep", "a.class")} {
		if _, err := os.Stat(filepath.Join(dir, kept)); err != nil {
			t.Errorf("%s was not copied: %v", kept, err)
		}
	}
	for _, hidden := range []string{"checker_main.py", "manager.in", "interactor_x.cpp"} {
		if _, err := os.Stat(filepath.Join(dir, hidden)); err == nil {
			t.Errorf("%s was copied into the run directory", hidden)
		}
	}
	// A file written into the copy does not appear in the original.
	if err := os.WriteFile(filepath.Join(dir, "note"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(work, "note")); err == nil {
		t.Error("the run directory is the work directory")
	}
}

func TestRunManager(t *testing.T) {
	work := t.TempDir()
	// Passes the message on reversed; rejects the message "bad"; dies on "boom".
	cmd := writeScript(t, work, `m=$(cat "$2")
[ "$m" = "bad" ] && exit 3
[ "$m" = "boom" ] && kill -9 $$
printf 'decode %s\n' "$m" | rev`)

	next, verdict, err := runManager(context.Background(), work, cmd, "in", "abc", "ans")
	if err != nil || verdict != "" || next != "cba edoced\n" {
		t.Fatalf("accepted message: next=%q verdict=%q err=%v", next, verdict, err)
	}
	if _, verdict, _ := runManager(context.Background(), work, cmd, "in", "bad", "ans"); verdict != VWA {
		t.Errorf("rejected message: %q, want WA", verdict)
	}
	if _, verdict, _ := runManager(context.Background(), work, cmd, "in", "boom", "ans"); verdict != VCheckerErr {
		t.Errorf("broken manager: %q, want %s", verdict, VCheckerErr)
	}
}

// The two runs: what each is given, and that they do not share a directory.
func TestTwoPass(t *testing.T) {
	work := t.TempDir()
	if err := os.WriteFile(filepath.Join(work, "prog"), []byte("x"), 0o755); err != nil {
		t.Fatal(err)
	}
	manager := writeScript(t, work, `printf 'second:'; cat "$2"`)
	calls := fakeSandbox(t, func(c sandboxCall) (*runOutcome, error) {
		if c.stdin == "first" {
			return &runOutcome{Stdout: "message", CPUMs: 40, PeakKB: 900}, nil
		}
		return &runOutcome{Stdout: "answer:" + c.stdin, CPUMs: 10, PeakKB: 2000}, nil
	})

	test := Test{Index: 1, Input: "first", Expected: "answer:second:message"}
	out, forced, err := twoPass(context.Background(), work, []string{"/box/prog"}, manager,
		test, Limits{TimeMS: 1000, MemoryKB: 262144}, 4000)
	if err != nil || forced != "" {
		t.Fatalf("forced=%q err=%v", forced, err)
	}
	if out.Stdout != "answer:second:message" {
		t.Errorf("run 2 got %q", out.Stdout)
	}
	if out.CPUMs != 40 || out.PeakKB != 2000 {
		t.Errorf("time/memory %d/%d, want the larger of each run: 40/2000", out.CPUMs, out.PeakKB)
	}
	if len(*calls) != 2 {
		t.Fatalf("%d sandbox runs, want 2", len(*calls))
	}
	first, second := (*calls)[0], (*calls)[1]
	if first.dir == second.dir || first.dir == work || second.dir == work {
		t.Errorf("runs share a directory: %s, %s (work %s)", first.dir, second.dir, work)
	}
	if _, err := os.Stat(first.dir); err == nil {
		t.Error("the directory of run 1 still exists")
	}
}

// Run 1 failing decides the test: the manager and run 2 never start.
func TestTwoPassStopsAfterAFailedFirstRun(t *testing.T) {
	work := t.TempDir()
	manager := writeScript(t, work, `exit 0`)
	calls := fakeSandbox(t, func(c sandboxCall) (*runOutcome, error) {
		return &runOutcome{ExitCode: 1}, nil
	})
	_, forced, err := twoPass(context.Background(), work, []string{"/box/prog"}, manager,
		Test{Index: 1, Input: "first"}, Limits{TimeMS: 1000}, 4000)
	if err != nil || forced != VREExit || len(*calls) != 1 {
		t.Fatalf("forced=%q err=%v runs=%d, want RE_EXIT after one run", forced, err, len(*calls))
	}
}

// A message the manager rejects is a wrong answer; run 2 never starts.
func TestTwoPassRejectedMessage(t *testing.T) {
	work := t.TempDir()
	manager := writeScript(t, work, `exit 1`)
	calls := fakeSandbox(t, func(c sandboxCall) (*runOutcome, error) {
		return &runOutcome{Stdout: "too long"}, nil
	})
	_, forced, err := twoPass(context.Background(), work, []string{"/box/prog"}, manager,
		Test{Index: 1, Input: "first"}, Limits{TimeMS: 1000}, 4000)
	if err != nil || forced != VWA || len(*calls) != 1 {
		t.Fatalf("forced=%q err=%v runs=%d, want WA after one run", forced, err, len(*calls))
	}
}
