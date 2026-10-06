package main

import (
	"context"
	"errors"
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

	itName, err := sourceName(it.Code, it.SourceFile)
	if err != nil {
		return VIE, nil, err
	}
	itSrc := filepath.Join(work, "interactor_"+itName)
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

	// Which side stopped first decides who is to blame (see
	// `interactiveVerdict`), so the two are awaited side by side.
	subDone := make(chan error, 1)
	itDone := make(chan error, 1)
	go func() { subDone <- sub.Wait() }()
	go func() { itDone <- interactor.Wait() }()
	var subErrRun, itErrRun error
	interactorFirst := false
	select {
	case subErrRun = <-subDone:
		itErrRun = <-itDone
	case itErrRun = <-itDone:
		interactorFirst = true
		if itErrRun != nil {
			// The dialogue is over and lost. The solution does not know:
			// its output goes to this process, not to the interactor, so
			// nothing tells it to stop — and once it has written more than
			// a pipe holds it blocks until the wall clock runs out.
			cancel()
		}
		subErrRun = <-subDone
	}
	wall := time.Since(start).Milliseconds()

	cpuUsec := cg.readInt("cpu.stat", "usage_usec")
	peak := cg.readInt("memory.peak", "")
	outcome := &runOutcome{
		Stderr: subErr.String(),
		CPUMs:  cpuUsec / 1000,
		WallMs: wall,
		PeakKB: peak / 1024,
	}

	timedOut := errors.Is(runCtx.Err(), context.DeadlineExceeded)
	return interactiveVerdict(timedOut, outcome.CPUMs, int64(job.Limits.TimeMS),
		subErrRun, itErrRun, interactorFirst), outcome, nil
}

// interactiveVerdict — the verdict of one dialogue, from how its two sides ended.
//
// The order matters and so does who stopped first. A rejected dialogue is
// a wrong answer whatever became of the solution afterwards: it was
// stopped by the judge (see the `cancel()` above) or ran on into the end
// of its input. Until 2026-10-07 the solution was left running, and one
// that kept writing after being rejected filled its pipe and was reported
// as IDLENESS five seconds later. A solution that dies on its own, before
// the interactor has said anything, is still a runtime error.
func interactiveVerdict(timedOut bool, cpuMs, limitMs int64, subErr, itErr error,
	interactorFirst bool) string {

	switch {
	case timedOut && cpuMs*4 < limitMs:
		// The wall clock ran out with the CPU idle: each side waited for
		// the other. The usual cause is a question that was never flushed.
		return VIdle
	case cpuMs > limitMs:
		return VTLE
	case interactorFirst && itErr != nil:
		return VWA
	case subErr != nil && !strings.Contains(subErr.Error(), "exit status"):
		return VIE
	case subErr != nil:
		return VRE
	case itErr == nil:
		return VAC
	default:
		return VWA
	}
}
