package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// runOutcome — bitta sandbox ishga tushirishning natijasi.
type runOutcome struct {
	Stdout   string
	Stderr   string
	ExitCode int
	CPUMs    int64 // CPU vaqti (user+sys) — TLE shu bo'yicha, wall clock bo'yicha EMAS
	WallMs   int64 // IDLENESS aniqlash uchun
	PeakKB   int64 // peak RSS
	OOMKill  bool
	Timeout  bool // wall clock chegarasi
	OutputEx bool // chiqish chegarasidan oshdi → OLE
}

// cgroup v2 subtree — CPU va xotira o'lchovining yagona ishonchli manbai.
// nsjail o'zi ham cheklaydi, lekin O'LCHASH uchun cgroup fayllarini o'qiymiz:
// wait4/rusage sandbox ichidagi nabira jarayonlarni to'liq qamramaydi.
const cgroupRoot = "/sys/fs/cgroup"

type cgroup struct{ path string }

func newCgroup(id string) (*cgroup, error) {
	p := filepath.Join(cgroupRoot, "rankwant", id)
	if err := os.MkdirAll(p, 0o755); err != nil {
		return nil, fmt.Errorf("cgroup yaratilmadi (cgroup v2 va yozish huquqi kerak): %w", err)
	}
	return &cgroup{path: p}, nil
}

func (c *cgroup) set(file, value string) error {
	return os.WriteFile(filepath.Join(c.path, file), []byte(value), 0o644)
}

func (c *cgroup) readInt(file, key string) int64 {
	data, err := os.ReadFile(filepath.Join(c.path, file))
	if err != nil {
		return 0
	}
	for _, line := range strings.Split(string(data), "\n") {
		if key == "" {
			if v, err := strconv.ParseInt(strings.TrimSpace(line), 10, 64); err == nil {
				return v
			}
			continue
		}
		if strings.HasPrefix(line, key+" ") {
			v, _ := strconv.ParseInt(strings.TrimSpace(strings.TrimPrefix(line, key+" ")), 10, 64)
			return v
		}
	}
	return 0
}

func (c *cgroup) remove() {
	_ = os.Remove(c.path)
}

// nsjailArgs — izolyatsiya konfiguratsiyasi.
// Har bir bayroq bake-off case'iga javob beradi (services/bakeoff/cases/).
func nsjailArgs(cg *cgroup, work string, lim Limits, wallSec int) []string {
	args := []string{
		"--quiet",
		"--mode", "o", // bir marta ishga tushir va chiq
		"--chroot", work, // 10-file-write: sandbox tashqarisi ko'rinmaydi
		"--cwd", "/",
		"--user", "65534", "--group", "65534", // 13-symlink: root emas
		"--hostname", "judge",
		"--disable_proc",       // 12-proc-read: host /proc yo'q
		"--iface_no_lo",        // 11-network: tarmoq interfeysi yo'q
		"--rlimit_fsize", "16", // MB — sandbox ichida ham fayl cheklovi
		"--rlimit_nofile", "64",
		"--time_limit", strconv.Itoa(wallSec), // wall chegarasi (IDLENESS uchun)
		"--use_cgroupv2",
		"--cgroupv2_mount", cg.path,
	}
	if lim.Processes > 0 {
		// 09-fork-bomb: cgroup pids.max — eng ishonchli to'siq
		args = append(args, "--cgroup_pids_max", strconv.Itoa(lim.Processes+4))
	}
	if lim.MemoryKB > 0 {
		args = append(args, "--cgroup_mem_max", strconv.FormatInt(int64(lim.MemoryKB)*1024, 10))
	}
	return args
}

// runSandboxed — buyruqni nsjail ostida ishga tushiradi va resurslarni o'lchaydi.
func runSandboxed(ctx context.Context, work string, cmd []string, stdin string,
	lim Limits, wallLimitMs int) (*runOutcome, error) {

	if len(cmd) == 0 {
		return nil, errors.New("bo'sh buyruq")
	}
	cg, err := newCgroup(fmt.Sprintf("%d", time.Now().UnixNano()))
	if err != nil {
		return nil, err
	}
	defer cg.remove()

	// pids.max cgroup darajasida ham — nsjail bayrog'iga qo'shimcha himoya
	if lim.Processes > 0 {
		_ = cg.set("pids.max", strconv.Itoa(lim.Processes+4))
	}
	if lim.MemoryKB > 0 {
		_ = cg.set("memory.max", strconv.FormatInt(int64(lim.MemoryKB)*1024, 10))
	}

	wallSec := (wallLimitMs + 999) / 1000
	if wallSec < 1 {
		wallSec = 1
	}
	args := append(nsjailArgs(cg, work, lim, wallSec), "--")
	args = append(args, cmd...)

	// Wall clock uchun qattiq to'xtatgich — nsjail ilinib qolsa ham
	runCtx, cancel := context.WithTimeout(ctx, time.Duration(wallSec+3)*time.Second)
	defer cancel()

	proc := exec.CommandContext(runCtx, "nsjail", args...)
	proc.Stdin = strings.NewReader(stdin)
	var out, errb capBuffer
	out.limit = int64(lim.OutputKB) * 1024
	errb.limit = 64 * 1024
	proc.Stdout = &out
	proc.Stderr = &errb

	start := time.Now()
	runErr := proc.Run()
	wall := time.Since(start).Milliseconds()

	exit := 0
	if runErr != nil {
		var ee *exec.ExitError
		if errors.As(runErr, &ee) {
			exit = ee.ExitCode()
		} else {
			exit = -1
		}
	}

	// CPU va peak RSS — cgroup v2 dan
	cpuUsec := cg.readInt("cpu.stat", "usage_usec")
	peak := cg.readInt("memory.peak", "")
	if peak == 0 {
		peak = cg.readInt("memory.max_usage_in_bytes", "")
	}
	oom := cg.readInt("memory.events", "oom_kill") > 0

	return &runOutcome{
		Stdout:   out.String(),
		Stderr:   errb.String(),
		ExitCode: exit,
		CPUMs:    cpuUsec / 1000,
		WallMs:   wall,
		PeakKB:   peak / 1024,
		OOMKill:  oom,
		OutputEx: out.Exceeded,
		Timeout:  runCtx.Err() != nil || wall >= int64(wallSec*1000),
	}, nil
}
