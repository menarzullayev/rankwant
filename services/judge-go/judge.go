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
	// Guruh bo'yicha: qaysi testlar o'tdi va qaysi guruh yiqildi.
	byGroup := map[int][]int{}
	failedGroup := map[int]bool{}

	// Tashqi checker bir marta tayyorlanadi — har testda qayta
	// kompilyatsiya vaqtni test soniga ko'paytirardi.
	var checkerCmd []string
	useChecker := job.Checker.Type == "special" || job.Checker.Type == "scorer"
	if useChecker {
		if job.Checker.Program == nil {
			res.Verdict = VIE
			res.CompileOutput = "checker dasturi berilmagan"
			return res
		}
		var err error
		if checkerCmd, err = prepareChecker(ctx, work, job.Checker.Program); err != nil {
			res.Verdict = VCheckerErr
			res.CompileOutput = err.Error()
			return res
		}
	}
	// `scorer` da har test o'z bahosini beradi, o'rtachasi olinadi.
	scoreSum := 0

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
		// Chiqish to'g'ri kelgan bo'lsa (dastur normal tugadi), yakuniy
		// so'z checkerniki: tenglik solishtiruvi maxsus masalada noto'g'ri.
		if useChecker && (v == VAC || v == VWA) {
			cv, err := runChecker(ctx, work, checkerCmd, job.Checker.Type,
				test.Input, out.Stdout, test.Expected)
			if err != nil {
				v = VIE
			} else {
				v = cv.Verdict
				scoreSum += cv.Score
			}
		}
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
			byGroup[test.Subtask] = append(byGroup[test.Subtask], test.Points)
			continue
		}
		worst = v
		failedGroup[test.Subtask] = true
		if res.FailedTestIndex == nil {
			idx := test.Index
			res.FailedTestIndex = &idx
		}
		if job.Mode != "ioi" {
			break // ACM: birinchi mag'lubiyatda to'xtaymiz
		}
	}

	res.TimeMS, res.MemoryKB = maxCPU, maxMem
	if job.Checker.Type == "scorer" && len(job.Tests) > 0 {
		// Mutlaq ball: testlar bo'yicha o'rtacha. Boshqalarning yechimiga
		// bog'liq emas, ya'ni qayta hisoblash zanjiri yo'q.
		res.Score = scoreSum / len(job.Tests)
	} else {
		res.Score = score(job, passed, byGroup, failedGroup)
	}

	// IOI: qisman ball olingan bo'lsa verdict PARTIAL — birinchi yiqilgan
	// testning verdicti emas. Aks holda 90 ball olgan yechim «WA» ko'rinardi.
	if (job.Mode == "ioi" || job.Checker.Type == "scorer") &&
		worst != VAC && worst != VIE && res.Score > 0 {
		worst = VPartial
	}
	res.Verdict = worst
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

// score — ballni rejimga qarab hisoblaydi.
//
// ACM: hammasi o'tsa 100, aks holda 0.
// IOI subtask bilan: har guruh o'z bali; `min` da guruh TO'LIQ o'tsagina
// beriladi (odatiy IOI), `sum` da o'tgan testlarning ballari yig'iladi.
// Subtasksiz IOI: o'tgan testlar ulushi — eski xatti-harakat saqlanadi.
func score(job *Job, passed int, byGroup map[int][]int, failedGroup map[int]bool) int {
	if len(job.Tests) == 0 {
		return 0
	}
	if job.Mode != "ioi" {
		if passed == len(job.Tests) {
			return 100
		}
		return 0
	}
	if len(job.Subtasks) == 0 {
		return passed * 100 / len(job.Tests)
	}

	total := 0
	for _, st := range job.Subtasks {
		if st.Scoring == "sum" {
			for _, p := range byGroup[st.ID] {
				total += p
			}
			continue
		}
		if !failedGroup[st.ID] {
			total += st.Points
		}
	}
	return total
}
