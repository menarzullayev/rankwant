package main

import (
	"context"
	"log/slog"
	"os"
	"os/exec"
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
	// Sandbox ichida PATH bo'yicha qidiruv yo'q — birinchi element MUTLAQ
	// yo'l bo'lishi shart, aks holda execve ENOENT beradi. Til ta'rifi
	// "g++" deb yozilishi mumkin, shuning uchun jail'ga kirishdan oldin hal qilamiz.
	if len(out) > 0 && !strings.HasPrefix(out[0], "/") {
		if abs, err := exec.LookPath(out[0]); err == nil {
			out[0] = abs
		}
	}
	return out
}

// judge — bitta job ni to'liq bajaradi.
func judge(ctx context.Context, job *Job, tests *store) *Result {
	t0 := time.Now()
	res := &Result{JobID: job.JobID, AttemptID: job.AttemptID, CustomRunID: job.CustomRunID,
		Verdict: VIE, PerTest: []TestResult{},
		Meta: JudgeMeta{Worker: "judge-go", Sandbox: "nsjail"}}

	// Testsiz job — sozlama xatosi. Bunday holatda "hammasi o'tdi" deb
	// AC qaytarish masalani yechilgan deb ko'rsatib qo'yardi.
	if len(job.Tests) == 0 && job.Mode != "custom" {
		slog.Error("job testsiz keldi", "job", job.JobID)
		return res
	}

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
		// Kompilyatsiya O'Z CPU byudjetidan foydalanadi. Aks holda
		// masalaning ish vaqti limiti (masalan 500 ms) g++ ga qo'llanib,
		// har bir C++ submission CE bo'lib qoladi.
		cl.TimeMS = job.Limits.CompileTimeMS
		out, err := runSandboxed(ctx, work, subst(job.Language.Compile, "/box/"+src, "/box/prog"),
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

	runCmd := subst(job.Language.Run, "/box/"+src, "/box/prog")

	// ── Interactive masala ─────────────────────────────────────────
	if job.Checker.Type == "interactive" {
		verdict, out, err := runInteractive(ctx, work, job, runCmd)
		if err != nil {
			res.Verdict = VIE
			res.CompileOutput = err.Error()
		} else {
			res.Verdict = verdict
			if out != nil {
				res.TimeMS, res.MemoryKB = out.CPUMs, out.PeakKB
			}
			if verdict == VAC {
				res.Score = 100
			}
		}
		res.Meta.TotalMS = time.Since(t0).Milliseconds()
		return res
	}

	// ── Testlar ────────────────────────────────────────────────────
	// Wall chegarasi CPU chegarasidan kattaroq: farqi IDLENESS ni ochib beradi.
	wallLimit := job.Limits.TimeMS*3 + 1000

	worst := VAC
	var maxCPU, maxMem int64
	passed := 0

	for _, test := range job.Tests {
		// Havola yechilmasa IE qaytaramiz. Ilgari bo'sh test bilan davom
		// etilardi va HAR submission WA olardi — sabab ko'rinmasdan.
		if err := resolve(ctx, &test, tests); err != nil {
			slog.Error("test ma'lumotini olish", "job", job.JobID, "test", test.Index, "err", err)
			worst = VIE
			break
		}
		out, err := runSandboxed(ctx, work, runCmd, test.Input, job.Limits, wallLimit)
		if err != nil {
			worst = VIE
			break
		}
		v := classify(out, test, job.Limits)
		// Custom rejimda javob solishtirilmaydi: dastur muvaffaqiyatli
		// tugagan bo'lsa AC, va chiqish foydalanuvchiga qaytariladi.
		var stdout string
		if job.Mode == "custom" {
			stdout = out.Stdout
			if v == VWA {
				v = VAC
			}
		}

		if out.CPUMs > maxCPU {
			maxCPU = out.CPUMs
		}
		if out.PeakKB > maxMem {
			maxMem = out.PeakKB
		}
		res.PerTest = append(res.PerTest, TestResult{
			Index: test.Index, Verdict: v, TimeMS: out.CPUMs,
			MemoryKB: out.PeakKB, Stdout: stdout})

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

// resolve test ma'lumotini S3 dan oladi. Inline `input`/`expected`
// berilgan bo'lsa (bake-off harness), S3 ga umuman murojaat qilinmaydi.
func resolve(ctx context.Context, test *Test, tests *store) error {
	for _, field := range []struct {
		ref string
		dst *string
	}{
		{test.InputRef, &test.Input},
		{test.ExpectedRef, &test.Expected},
	} {
		if *field.dst != "" || field.ref == "" {
			continue
		}
		data, err := tests.get(ctx, field.ref)
		if err != nil {
			return err
		}
		*field.dst = string(data)
	}
	return nil
}
