package main

import (
	"context"
	"slices"
	"strings"
	"testing"
)

// flagValue returns the argument after flag, or "" when the flag is absent.
func flagValue(args []string, flag string) string {
	if i := slices.Index(args, flag); i >= 0 && i+1 < len(args) {
		return args[i+1]
	}
	return ""
}

// The mask stays the default: a language must ask for its own procfs.
func TestNsjailArgsMaskProcByDefault(t *testing.T) {
	args := nsjailArgs("/tmp/work", Limits{TimeMS: 1000}, 3)

	if flagValue(args, "--tmpfsmount") != "/proc" {
		t.Fatalf("/proc is not masked: %s", strings.Join(args, " "))
	}
	if slices.Contains(args, "--mount") {
		t.Fatalf("a procfs is mounted without ProcSelf: %s", strings.Join(args, " "))
	}
	if got := flagValue(args, "--rlimit_nofile"); got != "64" {
		t.Fatalf("--rlimit_nofile %q, 64 expected", got)
	}
}

// ProcSelf swaps the empty tmpfs for a procfs limited to the sandbox's own
// processes. `--disable_proc` must stay: without it nsjail mounts a full procfs.
func TestNsjailArgsProcSelfMountsOwnProcesses(t *testing.T) {
	args := nsjailArgs("/tmp/work", Limits{TimeMS: 1000, ProcSelf: true}, 3)

	if got := flagValue(args, "--mount"); got != "none:/proc:proc:subset=pid,hidepid=invisible" {
		t.Fatalf("--mount %q — the subset procfs was expected", got)
	}
	if !slices.Contains(args, "--disable_proc") {
		t.Fatal("--disable_proc is gone: nsjail would mount a full procfs")
	}
	if flagValue(args, "--tmpfsmount") == "/proc" {
		t.Fatal("the tmpfs mask is still mounted over /proc")
	}
}

func TestNsjailArgsOpenFiles(t *testing.T) {
	args := nsjailArgs("/tmp/work", Limits{TimeMS: 1000, OpenFiles: 256}, 3)
	if got := flagValue(args, "--rlimit_nofile"); got != "256" {
		t.Fatalf("--rlimit_nofile %q, 256 expected", got)
	}
}

// ProcSelf follows the language into every run; the raised file limit is for
// the compiler only.
func TestJudgeCarriesProcSelfAndCompilerFiles(t *testing.T) {
	calls := fakeSandbox(t, func(sandboxCall) (*runOutcome, error) {
		return &runOutcome{Stdout: "3\n"}, nil
	})
	job := kotlinJob()
	job.Language.ProcSelf = true

	if res := judge(context.Background(), job, nil); res.Verdict != VAC {
		t.Fatalf("verdict %s, AC expected", res.Verdict)
	}
	compile, run := (*calls)[0].lim, (*calls)[1].lim
	if !compile.ProcSelf || !run.ProcSelf {
		t.Fatalf("ProcSelf lost: compile %v, run %v", compile.ProcSelf, run.ProcSelf)
	}
	if compile.OpenFiles != compileOpenFiles {
		t.Fatalf("compile OpenFiles %d, %d expected", compile.OpenFiles, compileOpenFiles)
	}
	if run.OpenFiles != 0 {
		t.Fatalf("the solution got OpenFiles %d — only the compiler may", run.OpenFiles)
	}
}

// R and PowerShell refuse to start with 64 open files; their row raises it
// for the runs, and the compiler keeps whichever limit is larger.
func TestJudgeCarriesLanguageOpenFiles(t *testing.T) {
	for _, want := range []struct{ language, compile, run int }{
		{0, compileOpenFiles, 0},
		{256, compileOpenFiles, 256},
		{1024, 1024, 1024},
	} {
		calls := fakeSandbox(t, func(sandboxCall) (*runOutcome, error) {
			return &runOutcome{Stdout: "3\n"}, nil
		})
		job := kotlinJob()
		job.Language.OpenFiles = want.language

		judge(context.Background(), job, nil)

		if got := (*calls)[0].lim.OpenFiles; got != want.compile {
			t.Fatalf("language %d: compile OpenFiles %d, %d expected", want.language, got, want.compile)
		}
		if got := (*calls)[1].lim.OpenFiles; got != want.run {
			t.Fatalf("language %d: run OpenFiles %d, %d expected", want.language, got, want.run)
		}
	}
}

func TestJudgeKeepsProcMaskedWithoutProcSelf(t *testing.T) {
	calls := fakeSandbox(t, func(sandboxCall) (*runOutcome, error) {
		return &runOutcome{Stdout: "3\n"}, nil
	})

	judge(context.Background(), kotlinJob(), nil)

	for i, c := range *calls {
		if c.lim.ProcSelf {
			t.Fatalf("sandbox call %d got ProcSelf for a language without it", i)
		}
	}
}

func TestValidatorCarriesProcSelf(t *testing.T) {
	calls := fakeSandbox(t, rejectsZero)
	job := validatedJob("1 2\n")
	job.Validator.ProcSelf = true

	judge(context.Background(), job, nil)

	validator, submission := partition(*calls)
	if len(validator) == 0 || !validator[0].lim.ProcSelf {
		t.Fatal("the validator run did not get ProcSelf")
	}
	for _, c := range submission {
		if c.lim.ProcSelf {
			t.Fatal("the submission inherited the validator's ProcSelf")
		}
	}
}
