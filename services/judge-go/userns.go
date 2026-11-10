package main

// ADR-0046: the judge container is not privileged.
//
// Until 2026-11-10 the container ran with `privileged: true` and
// `cgroup: host`: every capability, no seccomp, the host's cgroup tree
// writable, and the sandboxed program running as host uid 0. Two things
// needed that, and both are done here instead, without it:
//
//  1. Per-run cgroup limits. A non-privileged container sees its cgroup
//     tree read-only, and its files belong to uid 0. The launcher (the
//     only stage that starts as root) clones the worker into a new user,
//     mount and cgroup namespace; there the worker mounts a writable view
//     of the container's own cgroup, builds the subtree it limits runs in,
//     hands that subtree to the judge user and drops to it.
//  2. nsjail's namespaces. nsjail creates its own user namespace as the
//     judge user, so the sandboxed program runs as uid 10001, not 0.
//
// Capabilities the launcher needs (measured 2026-11-10 by removing each in
// turn, see docs/07-adr/0046): SETUID and SETGID to write a two-line id
// map, SETFCAP to map uid 0 into the new namespace (the cgroup files are
// uid 0's). Nothing else. After the worker starts the launcher drops to
// the judge user too, so no process in the container keeps uid 0.

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
)

const (
	// The judge user. The image creates it (Dockerfile); the sandboxed
	// program runs as this uid outside its namespace.
	judgeUID = 10001
	judgeGID = 10001

	// JUDGE_USERNS=1 turns the launcher on (compose sets it). Without it
	// the binary runs as before, which is what `go run` and the tests use.
	usernsEnv = "JUDGE_USERNS"
	// The launcher marks the process it starts; the worker unsets it.
	stageEnv    = "RANKWANT_JUDGE_STAGE"
	stageWorker = "worker"
	// The worker's end of the shutdown pipe: the launcher closes the other
	// end on SIGTERM, or by exiting, and the worker drains and stops.
	shutdownFD = 3
)

// usernsEnabled — the container runs the launcher (ADR-0046).
func usernsEnabled() bool { return os.Getenv(usernsEnv) == "1" }

// runLauncher starts the worker in a new user, mount and cgroup namespace
// and never returns. It runs as PID 1 of the container, so it also reaps
// whatever gets orphaned under it (#441: 222 zombies without an init).
func runLauncher(log *slog.Logger) int {
	if os.Getuid() != 0 {
		log.Error("JUDGE_USERNS=1: konteyner root sifatida boshlanishi kerak — " +
			"cgroup delegatsiyasini faqat ishga tushirish bosqichi qura oladi (ADR-0046)")
		return 1
	}
	r, w, err := os.Pipe()
	if err != nil {
		log.Error("shutdown quvuri yaratilmadi", "err", err)
		return 1
	}
	self, err := os.Executable()
	if err != nil {
		self = "/proc/self/exe"
	}
	cmd := exec.Command(self, os.Args[1:]...)
	cmd.Args[0] = os.Args[0]
	cmd.Env = append(os.Environ(), stageEnv+"="+stageWorker)
	cmd.Stdout, cmd.Stderr = os.Stdout, os.Stderr
	cmd.ExtraFiles = []*os.File{r} // fd 3 == shutdownFD
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Cloneflags: syscall.CLONE_NEWUSER | syscall.CLONE_NEWNS | syscall.CLONE_NEWCGROUP,
		// uid 0 owns the cgroup files; the judge user takes them over.
		UidMappings: []syscall.SysProcIDMap{
			{ContainerID: 0, HostID: 0, Size: 1},
			{ContainerID: judgeUID, HostID: judgeUID, Size: 1},
		},
		GidMappings: []syscall.SysProcIDMap{
			{ContainerID: 0, HostID: 0, Size: 1},
			{ContainerID: judgeGID, HostID: judgeGID, Size: 1},
		},
		// The worker clears its supplementary groups (root's group 0)
		// before it drops; that needs setgroups allowed in the namespace.
		GidMappingsEnableSetgroups: true,
	}
	if err := cmd.Start(); err != nil {
		log.Error("worker yangi user namespace'da ishga tushmadi", "err", err)
		return 1
	}
	_ = r.Close()

	// The id maps are written; root is not needed any more.
	if err := dropToJudgeUser(); err != nil {
		log.Error("launcher judge foydalanuvchisiga tusha olmadi", "err", err)
		_ = cmd.Process.Kill()
		return 1
	}

	sigs := make(chan os.Signal, 2)
	signal.Notify(sigs, syscall.SIGTERM, syscall.SIGINT)
	go func() {
		<-sigs
		// EOF on the worker's end: it finishes the job it holds and stops.
		_ = w.Close()
	}()

	for {
		var ws syscall.WaitStatus
		pid, err := syscall.Wait4(-1, &ws, 0, nil)
		if errors.Is(err, syscall.EINTR) {
			continue
		}
		if err != nil {
			log.Error("worker kutilmadi", "err", err)
			return 1
		}
		if pid != cmd.Process.Pid {
			continue // an orphan, reaped
		}
		if ws.Exited() {
			return ws.ExitStatus()
		}
		return 128 + int(ws.Signal())
	}
}

// enterWorker runs first in the worker: as uid 0 of its own user namespace
// it builds the delegated cgroup subtree, then drops to the judge user.
// It returns the shutdown pipe (closed by the launcher on SIGTERM).
func enterWorker() (io.ReadCloser, error) {
	_ = os.Unsetenv(stageEnv)

	// Our mounts stay ours. A namespace owned by a less privileged user
	// namespace already gets its mounts as slaves; this makes it explicit.
	if err := syscall.Mount("", "/", "", syscall.MS_REC|syscall.MS_PRIVATE, ""); err != nil {
		return nil, fmt.Errorf("mount propagation: %w", err)
	}
	// A fresh cgroup2 mount in our cgroup namespace: rooted at the
	// container's cgroup and writable, unlike the read-only one Docker gives.
	// Straight on top of Docker's it is refused with EBUSY: same superblock,
	// same root, same mount point (measured 2026-11-10). A tmpfs in between
	// makes the mount point a different filesystem.
	const flags = syscall.MS_NOSUID | syscall.MS_NODEV | syscall.MS_NOEXEC | syscall.MS_RELATIME
	if err := syscall.Mount("tmpfs", cgroupRoot, "tmpfs", flags, "size=4k,mode=0755"); err != nil {
		return nil, fmt.Errorf("cgroup ustiga tmpfs qo'yilmadi: %w", err)
	}
	if err := syscall.Mount("cgroup2", cgroupRoot, "cgroup2", flags, ""); err != nil {
		return nil, fmt.Errorf("cgroup2 mount qilinmadi: %w", err)
	}
	if err := setupDelegatedCgroup(cgroupRoot, judgeUID, judgeGID, os.Getpid(), os.Lchown); err != nil {
		return nil, err
	}
	if err := dropToJudgeUser(); err != nil {
		return nil, err
	}
	return os.NewFile(shutdownFD, "shutdown"), nil
}

// setupDelegatedCgroup lays out the container's cgroup tree:
//
//	/            controllers on; no processes (cgroup v2 forbids both)
//	├── init/    everything that was in the container before (PID 1 …)
//	└── rankwant/   limits set here by root; delegated to the judge user
//	    ├── svc/    the worker itself
//	    └── <run>/  one per sandboxed run, made by the worker
//
// The worker has to live inside `rankwant`: moving a new process into a run
// cgroup needs write access to the common ancestor's `cgroup.procs`, and
// `rankwant` is the ancestor it owns. Every step tolerates a restart of the
// container (the tree may already be there).
func setupDelegatedCgroup(root string, uid, gid, self int, chown func(string, int, int) error) error {
	initCg := filepath.Join(root, "init")
	if err := mkdirExist(initCg); err != nil {
		return err
	}
	pids, err := readPids(filepath.Join(root, "cgroup.procs"))
	if err != nil {
		return err
	}
	for _, pid := range pids {
		// A process may exit between the read and the move: ESRCH is fine.
		if err := writeFile(filepath.Join(initCg, "cgroup.procs"), strconv.Itoa(pid)); err != nil &&
			!errors.Is(err, syscall.ESRCH) {
			return fmt.Errorf("jarayon %d init/ ga ko'chirilmadi: %w", pid, err)
		}
	}
	if err := writeFile(filepath.Join(root, "cgroup.subtree_control"), "+cpu +memory +pids"); err != nil {
		return fmt.Errorf("ildiz subtree_control: %w", err)
	}
	parent := filepath.Join(root, "rankwant")
	if err := mkdirExist(parent); err != nil {
		return err
	}
	if err := writeFile(filepath.Join(parent, "cgroup.subtree_control"), "+cpu +memory +pids"); err != nil {
		return fmt.Errorf("rankwant subtree_control: %w", err)
	}
	// The ceiling of every run together. Root writes it and keeps the
	// files, so a compromised worker cannot lift it.
	for file, value := range map[string]string{
		"pids.max":        parentPidsMax,
		"memory.max":      parentMemMaxStr,
		"memory.swap.max": "0",
	} {
		if err := writeFile(filepath.Join(parent, file), value); err != nil {
			return fmt.Errorf("rankwant/%s: %w", file, err)
		}
	}
	svc := filepath.Join(parent, "svc")
	if err := mkdirExist(svc); err != nil {
		return err
	}
	// Delegation as cgroup v2 defines it: the directory and the three files
	// that let the owner create children and move processes between them.
	// The limit files of `rankwant` itself stay root's.
	for _, path := range []string{
		parent,
		filepath.Join(parent, "cgroup.procs"),
		filepath.Join(parent, "cgroup.subtree_control"),
		filepath.Join(parent, "cgroup.threads"),
		svc,
		filepath.Join(svc, "cgroup.procs"),
	} {
		if err := chown(path, uid, gid); err != nil {
			return fmt.Errorf("%s delegatsiya qilinmadi: %w", path, err)
		}
	}
	if err := writeFile(filepath.Join(svc, "cgroup.procs"), strconv.Itoa(self)); err != nil {
		return fmt.Errorf("worker rankwant/svc ga ko'chirilmadi: %w", err)
	}
	return nil
}

// dropToJudgeUser leaves uid 0 for good. Go applies set*id to every thread;
// leaving uid 0 clears the permitted and effective capability sets.
func dropToJudgeUser() error {
	if err := syscall.Setgroups([]int{}); err != nil {
		return fmt.Errorf("setgroups: %w", err)
	}
	if err := syscall.Setresgid(judgeGID, judgeGID, judgeGID); err != nil {
		return fmt.Errorf("setresgid: %w", err)
	}
	if err := syscall.Setresuid(judgeUID, judgeUID, judgeUID); err != nil {
		return fmt.Errorf("setresuid: %w", err)
	}
	return nil
}

// PreflightIdentity — fail closed: with the launcher on, the worker must
// not be root and must hold no capability. A worker that kept them would
// turn a sandbox escape back into what `privileged` was.
func PreflightIdentity() error {
	if os.Getuid() == 0 || os.Geteuid() == 0 {
		return fmt.Errorf("worker uid %d/%d — root bo'lmasligi kerak", os.Getuid(), os.Geteuid())
	}
	data, err := os.ReadFile("/proc/self/status")
	if err != nil {
		return fmt.Errorf("/proc/self/status o'qilmadi: %w", err)
	}
	eff, err := capEff(string(data))
	if err != nil {
		return err
	}
	if eff != 0 {
		return fmt.Errorf("worker capability ushlab turibdi: CapEff=%016x", eff)
	}
	return nil
}

// capEff parses the effective capability mask out of /proc/<pid>/status.
func capEff(status string) (uint64, error) {
	sc := bufio.NewScanner(strings.NewReader(status))
	for sc.Scan() {
		line := sc.Text()
		if v, ok := strings.CutPrefix(line, "CapEff:"); ok {
			return strconv.ParseUint(strings.TrimSpace(v), 16, 64)
		}
	}
	return 0, errors.New("CapEff qatori topilmadi")
}

func mkdirExist(path string) error {
	if err := os.Mkdir(path, 0o755); err != nil && !errors.Is(err, os.ErrExist) {
		return fmt.Errorf("%s yaratilmadi: %w", path, err)
	}
	return nil
}

// writeFile writes one value in one write, as cgroupfs expects. It never
// creates a file: a missing one means the controller is not there.
func writeFile(path, value string) error {
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_TRUNC, 0)
	if err != nil {
		return err
	}
	_, werr := f.WriteString(value)
	cerr := f.Close()
	if werr != nil {
		return werr
	}
	return cerr
}

func readPids(path string) ([]int, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("%s o'qilmadi: %w", path, err)
	}
	var pids []int
	for _, field := range strings.Fields(string(data)) {
		pid, err := strconv.Atoi(field)
		if err != nil {
			return nil, fmt.Errorf("%s: %q pid emas", path, field)
		}
		pids = append(pids, pid)
	}
	return pids, nil
}
