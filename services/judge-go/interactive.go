package main

import (
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// runInteractive — interactive masala: submission va interactor o'zaro
// bog'langan quvurlar orqali gaplashadi.
//
//	submission.stdout ──▶ interactor.stdin
//	interactor.stdout ──▶ submission.stdin
//
// Interactor ISHONCHLI (masala bilan keladi) va sandbox tashqarisida ishlaydi.
// Submission har doimgidek nsjail ostida.
//
// Verdict interactor ning chiqish kodidan olinadi: 0 = AC, aks holda WA.
// Ikkalasi ham kutib qolsa (deadlock) — IDLENESS.
func runInteractive(ctx context.Context, work string, job *Job,
	runCmd []string) (verdict string, out *runOutcome, err error) {

	it := job.Checker.Interactor
	if it == nil {
		return VIE, nil, fmt.Errorf("interactive masala, lekin interactor berilmagan")
	}

	itSrc := filepath.Join(work, "interactor_"+srcName(it.Code))
	if err := os.WriteFile(itSrc, []byte(it.Source), 0o644); err != nil {
		return VIE, nil, err
	}

	wallLimit := job.Limits.TimeMS*3 + 2000
	runCtx, cancel := context.WithTimeout(ctx, time.Duration(wallLimit)*time.Millisecond)
	defer cancel()

	// Interactor — ishonchli, sandboxsiz.
	itCmd := subst(it.Run, itSrc, itSrc)
	interactor := exec.CommandContext(runCtx, itCmd[0], itCmd[1:]...)

	subToInt, err := interactor.StdinPipe()
	if err != nil {
		return VIE, nil, err
	}
	intToSub, err := interactor.StdoutPipe()
	if err != nil {
		return VIE, nil, err
	}
	var itErr capBuffer
	itErr.limit = 64 * 1024
	interactor.Stderr = &itErr

	if err := interactor.Start(); err != nil {
		return VIE, nil, err
	}

	// Submission — sandbox ostida, quvurlar interactor bilan bog'langan.
	sub, cg, cleanup, err := startSandboxed(runCtx, work, runCmd, job.Limits, wallLimit)
	if err != nil {
		_ = interactor.Process.Kill()
		return VIE, nil, err
	}
	defer cleanup()

	sub.Stdin = intToSub
	subOut, err := sub.StdoutPipe()
	if err != nil {
		return VIE, nil, err
	}
	var subErr capBuffer
	subErr.limit = 64 * 1024
	sub.Stderr = &subErr

	start := time.Now()
	if err := sub.Start(); err != nil {
		_ = interactor.Process.Kill()
		return VIE, nil, err
	}

	go func() {
		_, _ = io.Copy(subToInt, subOut)
		_ = subToInt.Close() // submission tugadi — interactor EOF ko'rsin
	}()

	subErrRun := sub.Wait()
	itErrRun := interactor.Wait()
	wall := time.Since(start).Milliseconds()

	cpuUsec := cg.readInt("cpu.stat", "usage_usec")
	peak := cg.readInt("memory.peak", "")
	outcome := &runOutcome{
		Stderr: subErr.String(),
		CPUMs:  cpuUsec / 1000,
		WallMs: wall,
		PeakKB: peak / 1024,
	}

	switch {
	case runCtx.Err() != nil && outcome.CPUMs*4 < int64(job.Limits.TimeMS):
		// Wall tugadi, CPU sarflanmadi → ikkalasi bir-birini kutgan.
		return VIdle, outcome, nil
	case outcome.CPUMs > int64(job.Limits.TimeMS):
		return VTLE, outcome, nil
	case subErrRun != nil && !strings.Contains(subErrRun.Error(), "exit status"):
		return VIE, outcome, nil
	case subErrRun != nil:
		return VRE, outcome, nil
	case itErrRun == nil:
		return VAC, outcome, nil
	default:
		return VWA, outcome, nil
	}
}
