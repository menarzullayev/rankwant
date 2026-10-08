package main

import (
	"context"
	"io"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// Task kind "two_pass" (ADR-0053): the submission runs twice on every test.
//
//	run 1:  stdin = the test input          → stdout = a message
//	manager <input> <message> <jury>        → stdout = the input of run 2
//	run 2:  stdin = what the manager wrote  → stdout = the answer
//
// The answer of run 2 is then graded as on any problem — by comparison or
// by a special checker. The manager is the author's program and is trusted
// like a checker; it is what stands between the two runs (it shuffles,
// truncates, corrupts — whatever the problem is about) and it rejects a
// message that breaks the problem's rules by exiting non-zero.
//
// Nothing but the manager's output may travel from run 1 to run 2. The
// work directory is bind-mounted writable into the sandbox, so a file left
// there by run 1 would be read by run 2; each run therefore gets its own
// fresh copy of the compiled directory, removed afterwards.

// trustedPrefixes — files of the author's programs in the work directory.
// They are not copied into a run's directory: a submission has no business
// reading the checker.
var trustedPrefixes = []string{"checker", "manager", "interactor"}

// cloneForRun copies the compiled work directory for one run.
func cloneForRun(work string) (string, error) {
	dst, err := os.MkdirTemp("", "rw-pass-*")
	if err != nil {
		return "", err
	}
	err = filepath.WalkDir(work, func(path string, entry fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(work, path)
		if rel == "." {
			return nil
		}
		top := strings.SplitN(filepath.ToSlash(rel), "/", 2)[0]
		for _, prefix := range trustedPrefixes {
			if strings.HasPrefix(top, prefix) {
				if entry.IsDir() {
					return filepath.SkipDir
				}
				return nil
			}
		}
		target := filepath.Join(dst, rel)
		info, err := entry.Info()
		if err != nil {
			return err
		}
		if entry.IsDir() {
			return os.MkdirAll(target, info.Mode().Perm())
		}
		if !info.Mode().IsRegular() {
			return nil // a link or a device has no place in a fresh run
		}
		return copyFile(path, target, info.Mode().Perm())
	})
	if err == nil {
		err = os.Chmod(dst, 0o777)
	}
	if err != nil {
		os.RemoveAll(dst)
		return "", err
	}
	return dst, nil
}

func copyFile(src, dst string, mode fs.FileMode) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.OpenFile(dst, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, mode)
	if err != nil {
		return err
	}
	if _, err := io.Copy(out, in); err != nil {
		out.Close()
		return err
	}
	return out.Close()
}

// runManager turns the message of run 1 into the input of run 2.
//
// `verdict` is empty when the message was accepted; otherwise it is the
// verdict of the test: WA when the manager rejected the message, and
// CHECKER_ERROR when the manager itself broke — the author's fault, which
// must not be written to the solver.
func runManager(ctx context.Context, work string, runCmd []string,
	input, message, jury string) (next string, verdict string, err error) {

	paths := map[string]string{"in": input, "out": message, "ans": jury}
	args := make([]string, 0, 3)
	for _, k := range []string{"in", "out", "ans"} {
		p := filepath.Join(work, "manager."+k)
		if err := os.WriteFile(p, []byte(paths[k]), 0o644); err != nil {
			return "", VIE, err
		}
		args = append(args, p)
	}

	rctx, cancel := context.WithTimeout(ctx, checkerWallMS*time.Millisecond)
	defer cancel()
	cmd := exec.CommandContext(rctx, runCmd[0], append(append([]string{}, runCmd[1:]...), args...)...)
	stdout, runErr := cmd.Output()
	if rctx.Err() != nil {
		return "", VCheckerErr, nil
	}
	if runErr == nil {
		return string(stdout), "", nil
	}
	if code := cmd.ProcessState.ExitCode(); code > 0 {
		return "", VWA, nil
	}
	return "", VCheckerErr, nil
}

// ranToTheEnd — the run produced output that may be judged or passed on.
// `classify` also compares with the jury's answer; for run 1 that half of
// its verdict means nothing, only the resource and runtime half does.
func ranToTheEnd(v string) bool {
	return v == VAC || v == VWA || v == VPE
}

// twoPass runs one test of a two-pass job.
//
// It returns the outcome to classify and, when the test is already decided
// (run 1 failed, or the manager rejected its message), the verdict. Time
// and memory are the larger of the two runs: each run has the whole limit.
func twoPass(ctx context.Context, work string, runCmd, managerCmd []string,
	test Test, limits Limits, wallLimit int) (*runOutcome, string, error) {

	runIn := func(stdin string) (*runOutcome, error) {
		dir, err := cloneForRun(work)
		if err != nil {
			return nil, err
		}
		defer os.RemoveAll(dir)
		return sandboxed(ctx, dir, runCmd, stdin, limits, wallLimit)
	}

	first, err := runIn(test.Input)
	if err != nil {
		return nil, "", err
	}
	if v := classify(first, test, limits); !ranToTheEnd(v) {
		return first, v, nil
	}
	next, verdict, err := runManager(ctx, work, managerCmd, test.Input, first.Stdout, test.Expected)
	if err != nil {
		return nil, "", err
	}
	if verdict != "" {
		return first, verdict, nil
	}

	second, err := runIn(next)
	if err != nil {
		return nil, "", err
	}
	if first.CPUMs > second.CPUMs {
		second.CPUMs = first.CPUMs
	}
	if first.PeakKB > second.PeakKB {
		second.PeakKB = first.PeakKB
	}
	return second, "", nil
}
