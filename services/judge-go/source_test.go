package main

import (
	"context"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"
)

// Compilers pick the language from the file extension and JVM languages want
// the class name in it, so a language must be able to name its own source file.
// Before this, every code outside cpp/py/java was written as `main.txt`.

func TestSourceNameUsesLanguageFile(t *testing.T) {
	for _, file := range []string{"main.kt", "Main.java", "main.fsx", "main_1.c", "prog.test.ml"} {
		got, err := sourceName("any", file)
		if err != nil || got != file {
			t.Fatalf("sourceName(%q) = %q, %v — the name itself was expected", file, got, err)
		}
	}
}

// Rows without a file name (the bake-off cases) keep the old mapping.
func TestSourceNameFallsBackToCodePrefix(t *testing.T) {
	for code, want := range map[string]string{"cpp23": "main.cpp", "py313": "main.py", "java21": "Main.java"} {
		got, err := sourceName(code, "")
		if err != nil || got != want {
			t.Fatalf("sourceName(%q, \"\") = %q, %v — %q expected", code, got, err, want)
		}
	}
}

// The name is joined onto the work directory. Anything but a bare file name
// could write outside it, so it must be refused, not cleaned up.
func TestSourceNameRejectsPaths(t *testing.T) {
	for _, file := range []string{
		"../main.cpp", "a/main.cpp", `a\main.cpp`, "/etc/passwd", ".bashrc", "main",
		"main..cpp", "main.cpp/", "..", ".", "main.c pp", "main.cpp\n",
	} {
		if got, err := sourceName("cpp23", file); err == nil {
			t.Fatalf("sourceName(%q) was accepted as %q", file, got)
		}
	}
}

func kotlinJob() *Job {
	return &Job{
		JobID: "source-file",
		Language: Language{
			Code:       "kotlin24",
			SourceFile: "main.kt",
			Compile:    []string{"/opt/kotlinc/bin/kotlinc", "{src}", "-include-runtime", "-d", "{bin}.jar"},
			Run:        []string{"/usr/bin/java", "-jar", "{bin}.jar"},
		},
		Source: "fun main() { println(3) }\n",
		Limits: Limits{CompileTimeMS: 10_000, TimeMS: 1_000, MemoryKB: 262_144,
			OutputKB: 1_024, Processes: 32},
		Tests:   []Test{{Index: 1, Input: "1 2\n", Expected: "3\n"}},
		Checker: Checker{Type: "standard"},
		Mode:    "acm",
	}
}

func TestJudgeWritesSourceUnderLanguageFile(t *testing.T) {
	missing := false
	calls := fakeSandbox(t, func(c sandboxCall) (*runOutcome, error) {
		if _, err := os.Stat(filepath.Join(c.dir, "main.kt")); err != nil {
			missing = true
		}
		return &runOutcome{Stdout: "3\n"}, nil
	})

	res := judge(context.Background(), kotlinJob(), nil)

	if res.Verdict != VAC {
		t.Fatalf("verdict %s, AC expected (compile output %q)", res.Verdict, res.CompileOutput)
	}
	if missing {
		t.Fatal("main.kt was not in the work directory when the sandbox ran")
	}
	if len(*calls) != 2 {
		t.Fatalf("%d sandbox calls, compile + one test expected", len(*calls))
	}
	compile := []string{"/opt/kotlinc/bin/kotlinc", "/box/main.kt", "-include-runtime", "-d", "/box/prog.jar"}
	if got := (*calls)[0].cmd; !slices.Equal(got, compile) {
		t.Fatalf("compile command %q, %q expected", got, compile)
	}
	run := []string{"/usr/bin/java", "-jar", "/box/prog.jar"}
	if got := (*calls)[1].cmd; !slices.Equal(got, run) {
		t.Fatalf("run command %q, %q expected", got, run)
	}
}

// A wrong row is an internal error, visible to the operator, and nothing runs.
func TestJudgeRefusesUnsafeSourceFile(t *testing.T) {
	calls := fakeSandbox(t, func(sandboxCall) (*runOutcome, error) {
		return &runOutcome{Stdout: "3\n"}, nil
	})
	job := kotlinJob()
	job.Language.SourceFile = "../main.kt"

	res := judge(context.Background(), job, nil)

	if res.Verdict != VIE {
		t.Fatalf("verdict %s, IE expected", res.Verdict)
	}
	if !strings.Contains(res.CompileOutput, "../main.kt") {
		t.Fatalf("the reason does not name the file: %q", res.CompileOutput)
	}
	if len(*calls) != 0 {
		t.Fatalf("the sandbox ran %d times for a refused job", len(*calls))
	}
}

func TestPrepareValidatorUsesProgramFile(t *testing.T) {
	calls := fakeSandbox(t, func(sandboxCall) (*runOutcome, error) { return &runOutcome{}, nil })
	dir := t.TempDir()
	prog := &TrustedProgram{Code: "kotlin24", SourceFile: "main.kt",
		Compile: []string{"/opt/kotlinc/bin/kotlinc", "{src}", "-d", "{bin}.jar"},
		Run:     []string{"/usr/bin/java", "-jar", "{bin}.jar"}, Source: "fun main() {}\n"}

	run, err := prepareValidator(context.Background(), dir, prog)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(dir, "main.kt")); err != nil {
		t.Fatalf("validator source was not written as main.kt: %v", err)
	}
	if got := (*calls)[0].cmd; !slices.Contains(got, "/box/main.kt") {
		t.Fatalf("compile command %q does not use /box/main.kt", got)
	}
	if want := []string{"/usr/bin/java", "-jar", "/box/prog.jar"}; !slices.Equal(run, want) {
		t.Fatalf("run command %q, %q expected", run, want)
	}
}

func TestTrustedProgramsRefuseUnsafeSourceFile(t *testing.T) {
	fakeSandbox(t, func(sandboxCall) (*runOutcome, error) { return &runOutcome{}, nil })
	bad := &TrustedProgram{Code: "py313", SourceFile: "../x.py", Run: []string{python, "{src}"}, Source: "print(1)\n"}

	if _, err := prepareValidator(context.Background(), t.TempDir(), bad); err == nil {
		t.Fatal("validator accepted ../x.py")
	}
	if _, err := prepareChecker(context.Background(), t.TempDir(), bad); err == nil {
		t.Fatal("checker accepted ../x.py")
	}
	job := kotlinJob()
	job.Checker = Checker{Type: "interactive", Interactor: bad}
	if verdict, _, err := runInteractive(context.Background(), t.TempDir(), job, []string{"/bin/true"}); err == nil || verdict != VIE {
		t.Fatalf("interactor accepted ../x.py: verdict %s, err %v", verdict, err)
	}
}
