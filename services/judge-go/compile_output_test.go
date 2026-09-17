package main

import (
	"context"
	"strings"
	"testing"
	"unicode/utf8"
)

// csc, `go tool compile` and fpc print their errors on stdout. Before this the
// judge reported stderr only, and a C# or Go submission with a compile error
// came back as CE with an empty reason (measured in the judge image).

func compileFails(t *testing.T, out *runOutcome) *Result {
	t.Helper()
	fakeSandbox(t, func(sandboxCall) (*runOutcome, error) { return out, nil })
	return judge(context.Background(), kotlinJob(), nil)
}

func TestCompileErrorOnStdoutIsReported(t *testing.T) {
	res := compileFails(t, &runOutcome{ExitCode: 1,
		Stdout: "/box/main.cs(1,1): error CS1022: Type or namespace definition, or end-of-file expected\n"})
	if res.Verdict != VCE || !strings.Contains(res.CompileOutput, "error CS1022") {
		t.Fatalf("verdict %s, compile output %q: the compiler's stdout was expected", res.Verdict, res.CompileOutput)
	}
}

func TestCompileOutputKeepsBothStreams(t *testing.T) {
	res := compileFails(t, &runOutcome{ExitCode: 1,
		Stdout: "[1 of 2] Compiling Main ( /box/main.hs, /box/main.o )\n",
		Stderr: "/box/main.hs:1:1: error: parse error on input\n"})
	want := "[1 of 2] Compiling Main ( /box/main.hs, /box/main.o )\n/box/main.hs:1:1: error: parse error on input"
	if res.CompileOutput != want {
		t.Fatalf("compile output %q, %q expected", res.CompileOutput, want)
	}
}

func TestCompileErrorOnStderrIsReported(t *testing.T) {
	res := compileFails(t, &runOutcome{ExitCode: 1, Stderr: "main.cpp:1:1: error: expected ';'\n"})
	if res.CompileOutput != "main.cpp:1:1: error: expected ';'" {
		t.Fatalf("compile output %q", res.CompileOutput)
	}
}

func TestCompileTimeoutReportsStdout(t *testing.T) {
	res := compileFails(t, &runOutcome{Timeout: true, Stdout: "Compiling main.pas\n"})
	if res.Verdict != VCTimeout || !strings.Contains(res.CompileOutput, "Compiling main.pas") {
		t.Fatalf("verdict %s, compile output %q", res.Verdict, res.CompileOutput)
	}
}

// A flood of warnings on stdout must not reach the database whole, and the cut
// must not leave half a UTF-8 character behind.
func TestCompileOutputIsBounded(t *testing.T) {
	flood := strings.Repeat("ogohlantirish: o‘zgaruvchi\n", 10_000)
	res := compileFails(t, &runOutcome{ExitCode: 1, Stdout: flood})
	if len(res.CompileOutput) > compileOutputLimit+len("\n…") {
		t.Fatalf("compile output is %d bytes, the limit is %d", len(res.CompileOutput), compileOutputLimit)
	}
	if !strings.HasPrefix(res.CompileOutput, "ogohlantirish") || !utf8.ValidString(res.CompileOutput) {
		head := res.CompileOutput
		if len(head) > 40 {
			head = head[:40]
		}
		t.Fatalf("the head of the output was not kept intact: %q", head)
	}
}

func TestValidatorCompileErrorOnStdoutIsReported(t *testing.T) {
	fakeSandbox(t, func(sandboxCall) (*runOutcome, error) {
		return &runOutcome{ExitCode: 1, Stdout: "validator.cs(3,5): error CS0103: The name 'x' does not exist\n"}, nil
	})
	prog := &TrustedProgram{Code: "cs", Run: []string{"{bin}"}, Source: "x\n",
		Compile: []string{"/usr/bin/csc", "{src}"}}
	_, err := prepareValidator(context.Background(), t.TempDir(), prog)
	if err == nil || !strings.Contains(err.Error(), "error CS0103") {
		t.Fatalf("the validator's compile error lost its reason: %v", err)
	}
}
