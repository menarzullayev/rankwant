package main

import (
	"os"
	"path/filepath"
	"testing"
)

func TestClassifyAnswerBothAcceptsStdout(t *testing.T) {
	lim := Limits{TimeMS: 1000, MemoryKB: 262144, OutputKB: 65536}
	test := Test{Expected: "3"}
	out := &runOutcome{ExitCode: 0, Stdout: "3"}
	if got := classifyAnswer(out, test, lim, t.TempDir(), IO{Mode: "both"}); got != VAC {
		t.Fatalf("stdout AC: got %q", got)
	}
}

func TestClassifyAnswerBothAcceptsOutputFile(t *testing.T) {
	lim := Limits{TimeMS: 1000, MemoryKB: 262144, OutputKB: 65536}
	test := Test{Expected: "42"}
	work := t.TempDir()
	if err := writeTestInputFile(work, Test{Input: "1 2"}, IO{Mode: "both"}); err != nil {
		t.Fatal(err)
	}
	if err := osWrite(work, "output.txt", "42"); err != nil {
		t.Fatal(err)
	}
	out := &runOutcome{ExitCode: 0, Stdout: "wrong"}
	if got := classifyAnswer(out, test, lim, work, IO{Mode: "both"}); got != VAC {
		t.Fatalf("file AC: got %q", got)
	}
}

func TestClassifyAnswerBothRejectsStaleOutputFile(t *testing.T) {
	lim := Limits{TimeMS: 1000, MemoryKB: 262144, OutputKB: 65536}
	test := Test{Expected: "99"}
	work := t.TempDir()
	if err := osWrite(work, "output.txt", "99"); err != nil {
		t.Fatal(err)
	}
	resetIOArtifacts(work, IO{Mode: "both"})
	out := &runOutcome{ExitCode: 0, Stdout: "1"}
	if got := classifyAnswer(out, test, lim, work, IO{Mode: "both"}); got != VWA {
		t.Fatalf("stale file removed: got %q", got)
	}
}

func osWrite(dir, name, body string) error {
	return os.WriteFile(filepath.Join(dir, name), []byte(body), 0o644)
}
