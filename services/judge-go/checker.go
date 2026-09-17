package main

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// Checker dasturi — `special` va `scorer` masalalarida javobni baholaydi.
//
// Interactor kabi u ham ISHONCHLI: masala bilan birga keladi, biz uni
// yozganmiz. Shu sababli sandboxsiz ishlaydi — sandbox submission uchun.
//
// Chaqirilishi testlib bilan bir xil:  checker <input> <output> <answer>
//
//	special: chiqish kodi 0 = AC, aks holda WA
//	scorer:  chiqishning OXIRGI qatorida 0–100 oralig'ida son
//
// Vaqt chegarasi qattiq: checker o'zi cheksiz aylanib qolsa butun
// navbatni to'xtatib qo'yardi.
const checkerWallMS = 10_000

type checkerVerdict struct {
	Verdict string
	Score   int
}

// prepareChecker — checker manbasini yozadi va kerak bo'lsa kompilyatsiya
// qiladi. Job boshida BIR MARTA chaqiriladi: har testda qayta qurish
// kompilyatsiya vaqtini test soniga ko'paytirardi.
func prepareChecker(ctx context.Context, work string, prog *TrustedProgram) ([]string, error) {
	name, err := sourceName(prog.Code, prog.SourceFile)
	if err != nil {
		return nil, err
	}
	src := filepath.Join(work, "checker_"+name)
	if err := os.WriteFile(src, []byte(prog.Source), 0o644); err != nil {
		return nil, err
	}
	bin := filepath.Join(work, "checker_bin")

	if len(prog.Compile) > 0 {
		cctx, cancel := context.WithTimeout(ctx, 30*time.Second)
		defer cancel()
		cmd := subst(prog.Compile, src, bin)
		out, err := exec.CommandContext(cctx, cmd[0], cmd[1:]...).CombinedOutput()
		if err != nil {
			return nil, fmt.Errorf("checker kompilyatsiyasi: %w: %s", err, string(out))
		}
	}
	return subst(prog.Run, src, bin), nil
}

// runChecker — bitta testni baholaydi.
func runChecker(ctx context.Context, work string, runCmd []string, kind string,
	input, output, answer string) (checkerVerdict, error) {

	paths := map[string]string{"in": input, "out": output, "ans": answer}
	args := make([]string, 0, 3)
	for _, k := range []string{"in", "out", "ans"} {
		p := filepath.Join(work, "checker."+k)
		if err := os.WriteFile(p, []byte(paths[k]), 0o644); err != nil {
			return checkerVerdict{Verdict: VIE}, err
		}
		args = append(args, p)
	}

	rctx, cancel := context.WithTimeout(ctx, checkerWallMS*time.Millisecond)
	defer cancel()

	cmd := exec.CommandContext(rctx, runCmd[0], append(append([]string{}, runCmd[1:]...), args...)...)
	stdout, err := cmd.Output()

	// Checker yiqilishi submission aybi EMAS — buni WA dan ajratamiz,
	// aks holda muallif xatosi o'quvchiga yozilardi.
	if rctx.Err() != nil {
		return checkerVerdict{Verdict: VCheckerErr}, nil
	}

	code := cmd.ProcessState.ExitCode()
	if kind == "scorer" {
		if err != nil && code < 0 {
			return checkerVerdict{Verdict: VCheckerErr}, nil
		}
		score, ok := lastNumber(string(stdout))
		if !ok {
			return checkerVerdict{Verdict: VCheckerErr}, nil
		}
		if score <= 0 {
			return checkerVerdict{Verdict: VWA, Score: 0}, nil
		}
		if score > 100 {
			score = 100
		}
		return checkerVerdict{Verdict: VAC, Score: score}, nil
	}

	if err == nil && code == 0 {
		return checkerVerdict{Verdict: VAC, Score: 100}, nil
	}
	if code < 0 {
		return checkerVerdict{Verdict: VCheckerErr}, nil
	}
	return checkerVerdict{Verdict: VWA}, nil
}

// lastNumber — chiqishning oxirgi bo'sh bo'lmagan qatoridan butun son.
func lastNumber(s string) (int, bool) {
	lines := strings.Split(strings.TrimSpace(s), "\n")
	for i := len(lines) - 1; i >= 0; i-- {
		f := strings.Fields(strings.TrimSpace(lines[i]))
		if len(f) == 0 {
			continue
		}
		if n, err := strconv.ParseFloat(f[len(f)-1], 64); err == nil {
			return int(n), true
		}
		return 0, false
	}
	return 0, false
}
