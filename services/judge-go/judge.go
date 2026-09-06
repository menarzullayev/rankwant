package main

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// normalise — standart checker: qatorlar oxiridagi bo'shliq va oxirgi bo'sh
// qatorlar e'tiborsiz. Bu ko'pchilik OJ ning odatiy xatti-harakati.
func normalise(s string) string {
	lines := strings.Split(strings.ReplaceAll(s, "\r\n", "\n"), "\n")
	for i := range lines {
		lines[i] = strings.TrimRight(lines[i], " \t")
	}
	for len(lines) > 0 && lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}
	return strings.Join(lines, "\n")
}

func srcName(langCode string) string {
	switch {
	case strings.HasPrefix(langCode, "cpp"), strings.HasPrefix(langCode, "c++"):
		return "main.cpp"
	case strings.HasPrefix(langCode, "py"):
		return "main.py"
	case strings.HasPrefix(langCode, "java"):
		return "Main.java"
	default:
		return "main.txt"
	}
}

func subst(args []string, src, bin string) []string {
	out := make([]string, len(args))
	for i, a := range args {
		a = strings.ReplaceAll(a, "{src}", src)
		out[i] = strings.ReplaceAll(a, "{bin}", bin)
	}
	return out
}

// judge — bitta job ni to'liq bajaradi.
func judge(ctx context.Context, job *Job) *Result {
	t0 := time.Now()
	res := &Result{JobID: job.JobID, Verdict: VIE, PerTest: []TestResult{},
		Meta: JudgeMeta{Worker: "judge-go", Sandbox: "nsjail"}}

	work, err := os.MkdirTemp("", "rw-judge-*")
	if err != nil {
		return res
	}
	defer os.RemoveAll(work)
	if err := os.Chmod(work, 0o777); err != nil {
		return res
	}

	setupStart := time.Now()
	src := srcName(job.Language.Code)
	if err := os.WriteFile(filepath.Join(work, src), []byte(job.Source), 0o644); err != nil {
		return res
	}
	res.Meta.SandboxSetupMS = time.Since(setupStart).Milliseconds()

	// ── Kompilyatsiya ───────────────────────────────────────────────
	if len(job.Language.Compile) > 0 {
		cl := job.Limits
		cl.MemoryKB = 1024 * 1024 // kompilyator uchun kengroq
		cl.Processes = 16
		out, err := runSandboxed(ctx, work, subst(job.Language.Compile, "/"+src, "/prog"),
			"", cl, job.Limits.CompileTimeMS)
		if err != nil {
			res.CompileOutput = err.Error()
			return res
		}
		if out.Timeout {
			res.Verdict, res.CompileOutput = VCTimeout, out.Stderr
			res.Meta.TotalMS = time.Since(t0).Milliseconds()
			return res
		}
		if out.ExitCode != 0 {
			res.Verdict, res.CompileOutput = VCE, out.Stderr
			res.Meta.TotalMS = time.Since(t0).Milliseconds()
			return res
		}
	}

	// ── Testlar ────────────────────────────────────────────────────
	runCmd := subst(job.Language.Run, "/"+src, "/prog")
	// Wall chegarasi CPU chegarasidan kattaroq: farqi IDLENESS ni ochib beradi.
	wallLimit := job.Limits.TimeMS*3 + 1000

	worst := VAC
	var maxCPU, maxMem int64
	passed := 0

	for _, test := range job.Tests {
		out, err := runSandboxed(ctx, work, runCmd, test.Input, job.Limits, wallLimit)
		if err != nil {
			worst = VIE
			break
		}
		v := classify(out, test, job.Limits)

		if out.CPUMs > maxCPU {
			maxCPU = out.CPUMs
		}
		if out.PeakKB > maxMem {
			maxMem = out.PeakKB
		}
		res.PerTest = append(res.PerTest, TestResult{
			Index: test.Index, Verdict: v, TimeMS: out.CPUMs, MemoryKB: out.PeakKB})

		if v == VAC {
			passed++
			continue
		}
		worst = v
		idx := test.Index
		res.FailedTestIndex = &idx
		if job.Mode != "ioi" {
			break // ACM: birinchi mag'lubiyatda to'xtaymiz
		}
	}

	res.Verdict = worst
	res.TimeMS, res.MemoryKB = maxCPU, maxMem
	if len(job.Tests) > 0 {
		res.Score = passed * 100 / len(job.Tests)
	}
	res.Meta.TotalMS = time.Since(t0).Milliseconds()
	return res
}

// classify — bitta test natijasini verdictga aylantiradi.
// Tartib muhim: xavfsizlik va resurs chegaralari to'g'ri javobdan OLDIN tekshiriladi.
func classify(out *runOutcome, test Test, lim Limits) string {
	switch {
	case out.OutputEx:
		return VOLE
	case out.OOMKill || (lim.MemoryKB > 0 && out.PeakKB >= int64(lim.MemoryKB)):
		return VMLE
	case out.CPUMs > int64(lim.TimeMS):
		return VTLE
	case out.Timeout:
		// Wall tugadi, lekin CPU sarflanmadi → dastur kutib qoldi, sikl aylanmadi.
		if out.CPUMs*4 < int64(lim.TimeMS) {
			return VIdle
		}
		return VTLE
	case out.ExitCode == 0:
		if normalise(out.Stdout) == normalise(test.Expected) {
			return VAC
		}
		return VWA
	default:
		// nsjail izolyatsiya qoidasini buzganda o'ldiradi; buni RE dan ajratamiz.
		if strings.Contains(out.Stderr, "Operation not permitted") ||
			strings.Contains(out.Stderr, "seccomp") ||
			out.ExitCode == 159 { // 128+31 (SIGSYS)
			return VSecurity
		}
		return VRE
	}
}
