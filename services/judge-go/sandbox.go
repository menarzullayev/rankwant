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
	"sync/atomic"
	"syscall"
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
const (
	cgroupRoot   = "/sys/fs/cgroup"
	cgroupParent = cgroupRoot + "/rankwant"

	// Ota cgroup darajasidagi mutlaq shift. Bola cgroup sozlashda xato
	// bo'lsa ham, portlash radiusi shu bilan chegaralanadi — host yiqilmaydi.
	parentPidsMax   = "512"
	parentMemMaxStr = "4294967296" // 4 GiB
)

type cgroup struct{ path string }

// ensureParent — /sys/fs/cgroup/rankwant ni yaratadi va BOLALAR uchun
// kerakli kontrollerlarni yoqadi.
//
// NEGA BU SHART: cgroup v2 da bola cgroup'da `pids.max` yoki `memory.max`
// fayllari OTA cgroup'ning `cgroup.subtree_control` iga tegishli kontroller
// yozilmagunicha UMUMAN YARATILMAYDI. MkdirAll bilan ikki darajani bir yo'la
// yaratsak, `rankwant` ning subtree_control i bo'sh qoladi va bola cgroup'da
// limit fayllari bo'lmaydi — ya'ni ishonchsiz kod CHEKLOVSIZ ishlaydi.
//
// Bu 2026-09-06 da host'ni ikki marta yiqitgan: fork bomb limitsiz ko'paydi,
// global OOM boshlandi, swap thrashing tizimni D-state ga tushirdi.
func ensureParent() error {
	if err := os.MkdirAll(cgroupParent, 0o755); err != nil {
		return fmt.Errorf("ota cgroup yaratilmadi: %w", err)
	}
	ctrl := filepath.Join(cgroupParent, "cgroup.subtree_control")
	if err := os.WriteFile(ctrl, []byte("+pids +memory +cpu"), 0o644); err != nil {
		return fmt.Errorf("subtree_control yozilmadi (%s): %w", ctrl, err)
	}
	// Ota darajasidagi shift — ikkinchi himoya qatlami.
	_ = os.WriteFile(filepath.Join(cgroupParent, "pids.max"), []byte(parentPidsMax), 0o644)
	_ = os.WriteFile(filepath.Join(cgroupParent, "memory.max"), []byte(parentMemMaxStr), 0o644)
	return nil
}

// newCgroup — bitta ishga tushirish uchun bola cgroup. Limit fayllari
// haqiqatan mavjudligini TEKSHIRADI; bo'lmasa xato qaytaradi.
func newCgroup(id string) (*cgroup, error) {
	if err := ensureParent(); err != nil {
		return nil, err
	}
	p := filepath.Join(cgroupParent, id)
	if err := os.MkdirAll(p, 0o755); err != nil {
		return nil, fmt.Errorf("bola cgroup yaratilmadi: %w", err)
	}
	cg := &cgroup{path: p}
	for _, f := range []string{"pids.max", "memory.max"} {
		if _, err := os.Stat(filepath.Join(p, f)); err != nil {
			cg.remove()
			return nil, fmt.Errorf("cgroup'da %s yo'q — kontrollerlar yoqilmagan, "+
				"ishonchsiz kod cheklovsiz ishlagan bo'lardi", f)
		}
	}
	return cg, nil
}

// set — xatoni QAYTARADI. Avval `_ =` bilan yutilar edi va limit
// qo'yilmagani bilinmasdi.
func (c *cgroup) set(file, value string) error {
	path := filepath.Join(c.path, file)
	if err := os.WriteFile(path, []byte(value), 0o644); err != nil {
		return fmt.Errorf("%s = %s yozilmadi: %w", file, value, err)
	}
	// Yozildi deb ishonmaymiz — qaytarib o'qib tasdiqlaymiz.
	got, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("%s qayta o'qilmadi: %w", file, err)
	}
	if strings.TrimSpace(string(got)) != value {
		return fmt.Errorf("%s tasdiqlanmadi: yozildi %q, o'qildi %q",
			file, value, strings.TrimSpace(string(got)))
	}
	return nil
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

// PreflightCgroup — worker ishga tushishida bir marta chaqiriladi.
// Limit qo'yish imkoniyati YO'Q bo'lsa, worker ishlamasligi kerak:
// cheklovsiz judge — bu host'ni yo'qotish demak.
func PreflightCgroup() error {
	cg, err := newCgroup("preflight")
	if err != nil {
		return err
	}
	defer cg.remove()
	if err := cg.set("pids.max", "16"); err != nil {
		return fmt.Errorf("pids.max qo'yib bo'lmadi: %w", err)
	}
	if err := cg.set("memory.max", "134217728"); err != nil {
		return fmt.Errorf("memory.max qo'yib bo'lmadi: %w", err)
	}
	return nil
}

// cpuLimitSec — RLIMIT_CPU soniyalarda; yuqoriga yaxlitlanadi va
// 1 soniya zaxira qo'shiladi, aks holda chegaraga yaqin AC lar noto'g'ri
// TLE bo'lib qolardi.
func cpuLimitSec(ms int) int {
	sec := (ms + 999) / 1000
	if sec < 1 {
		sec = 1
	}
	return sec + 1
}

// nsjailArgs — izolyatsiya konfiguratsiyasi.
// Har bir bayroq bake-off case'iga javob beradi (services/bakeoff/cases/).
func nsjailArgs(work string, lim Limits, wallSec int) []string {
	args := []string{
		"--quiet",
		"--mode", "o", // bir marta ishga tushir va chiq
		// Host ildizi READ-ONLY ko'rinadi — kompilyator va kutubxonalar kerak,
		// lekin yozib bo'lmaydi (10-file-write). Yoziladigan yagona joy — /box.
		"--chroot", "/",
		"--bindmount", work + ":/box",
		"--cwd", "/box",
		// KELISHUV: inside=65534, outside=0.
		// "65534:65534:1" ideal bo'lardi, lekin u newuidmap/subuid sozlamasini
		// talab qiladi; usiz nsjail o'z mount daraxtini qura olmaydi
		// ("mkdir(...): Permission denied"). Shuning uchun tashqi uid 0 qoladi.
		// Buni qoplaydigan qatlamlar: chroot / READ-ONLY, yoziladigan yagona
		// joy /box, tarmoq yo'q, /proc yo'q, cgroup chegaralari, va judge host
		// arxitektura darajasida izolyatsiya qilingan (06-architecture).
		"--user", "65534",
		"--group", "65534",
		"--hostname", "judge",
		// Jail ichida muhit o'zgaruvchilari BO'SH bo'ladi. PATH bo'lmasa g++
		// ishga tushadi, lekin collect2 'ld' ni topa olmay "cannot find 'ld'"
		// beradi — kompilyatsiya CE bo'lib ko'rinadi, aslida sabab boshqa.
		"--env", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
		"--env", "HOME=/box",
		"--env", "LANG=C.UTF-8",
		// 12-proc-read: --disable_proc faqat YANGI procfs mount'ini to'sadi.
		// --chroot / bo'lgani uchun HOST /proc jail ichiga kirib keladi va
		// /proc/1/cmdline o'qiladi. Ustiga bo'sh tmpfs qo'yib niqoblaymiz.
		"--disable_proc",
		"--tmpfsmount", "/proc",
		"--iface_no_lo",        // 11-network: tarmoq interfeysi yo'q
		"--rlimit_fsize", "16", // MB — sandbox ichida ham fayl cheklovi
		"--rlimit_nofile", "64",
		// RLIMIT_AS — VIRTUAL manzil fazosi, haqiqiy xotira emas. Haqiqiy
		// chegara cgroup `memory.max` da va MLE ham o'shandan o'lchanadi,
		// ya'ni bu bayroq himoyaning asosi emas.
		//
		// nsjail standarti 4096 MB. JVM esa ishga tushishda metaspace va
		// siqilgan class space uchun bir necha GB ni TEGMASDAN rezervlaydi,
		// natijada har bir Java yuborishi «insufficient memory for the Java
		// Runtime Environment» bilan yiqilardi — o'lchandi: 4096 da javac
		// yiqiladi, 8192 dan boshlab o'tadi.
		"--rlimit_as", "16384",
		"--time_limit", strconv.Itoa(wallSec), // wall chegarasi (IDLENESS uchun)
		// RLIMIT_CPU — kernel jarayonni CPU limitida O'ZI to'xtatadi.
		// Busiz TLE submission wall chegarasigacha (3×) ishlaydi: 500ms limitli
		// masala 3s judge vaqtini yeydi. Contest yuklamasida bu o'tkazuvchanlikni
		// uchdan biriga tushiradi. Aniqlik 1 soniya — shuning uchun bu
		// CHEGARA, o'lchov emas; aniq verdict baribir cpu.stat bo'yicha beriladi.
		"--rlimit_cpu", strconv.Itoa(cpuLimitSec(lim.TimeMS)),

		// DIQQAT: nsjail'ning O'Z cgroup boshqaruvi (--use_cgroupv2) ATAYLAB
		// ishlatilmaydi. U jarayonni ROOT ostidagi yangi NSJAIL.<pid> guruhiga
		// ko'chiradi, ya'ni bizning o'lchov subtree'imizdan CHIQIB KETADI va
		// cpu.stat/memory.peak nolga yaqin o'qiladi — TLE IDLENESS bo'lib,
		// MLE esa WA bo'lib ko'rinadi.
		//
		// Shuning uchun cheklash HAM, o'lchash HAM bizning cgroup'imizda:
		// nsjail bolani UseCgroupFD orqali to'g'ridan-to'g'ri unga tug'diradi,
		// memory.max va pids.max esa runSandboxed ichida yoziladi.
	}
	if lim.Processes > 0 {
		// 09-fork-bomb: cgroup pids.max dan tashqari har jarayon uchun rlimit.
		args = append(args, "--rlimit_nproc", strconv.Itoa(lim.Processes+4))
	}
	return args
}

// startSandboxed — sandbox'li jarayonni TAYYORLAB beradi, lekin ishga
// tushirmaydi va kutmaydi. Interactive masalalarda quvurlarni ulash uchun
// kerak: chaqiruvchi Stdin/Stdout ni o'zi biriktiradi.
//
// Qaytaradi: cmd, o'lchov uchun cgroup, tozalash funksiyasi.
func startSandboxed(ctx context.Context, work string, cmd []string,
	lim Limits, wallLimitMs int) (*exec.Cmd, *cgroup, func(), error) {

	if len(cmd) == 0 {
		return nil, nil, func() {}, errors.New("bo'sh buyruq")
	}
	cg, err := newCgroup(fmt.Sprintf("i%d", time.Now().UnixNano()))
	if err != nil {
		return nil, nil, func() {}, err
	}
	cleanup := func() { cg.remove() }

	if err := applyLimits(cg, lim); err != nil {
		cleanup()
		return nil, nil, func() {}, err
	}

	wallSec := (wallLimitMs + 999) / 1000
	if wallSec < 1 {
		wallSec = 1
	}
	args := append(nsjailArgs(work, lim, wallSec), "--")
	args = append(args, cmd...)

	proc := exec.CommandContext(ctx, "nsjail", args...)
	if fd, err := os.Open(cg.path); err == nil {
		proc.SysProcAttr = &syscall.SysProcAttr{UseCgroupFD: true, CgroupFD: int(fd.Fd())}
		cleanup = func() { fd.Close(); cg.remove() }
	}
	return proc, cg, cleanup, nil
}

// applyLimits — limitlarni cgroup'ga yozadi. Xato bo'lsa QAYTARADI:
// limitsiz ishonchsiz kod ishga tushmasligi kerak.
func applyLimits(cg *cgroup, lim Limits) error {
	pids := "64"
	if lim.Processes > 0 {
		pids = strconv.Itoa(lim.Processes + 4)
	}
	if err := cg.set("pids.max", pids); err != nil {
		return fmt.Errorf("jarayon limiti qo'yilmadi: %w", err)
	}
	if lim.MemoryKB > 0 {
		if err := cg.set("memory.max", strconv.FormatInt(int64(lim.MemoryKB)*1024, 10)); err != nil {
			return fmt.Errorf("xotira limiti qo'yilmadi: %w", err)
		}
	}
	if err := cg.set("memory.swap.max", "0"); err != nil {
		return fmt.Errorf("swap limiti qo'yilmadi: %w", err)
	}
	return nil
}

// sandboxRun — runSandboxed imzosi.
type sandboxRun func(ctx context.Context, work string, cmd []string, stdin string,
	lim Limits, wallLimitMs int) (*runOutcome, error)

// sandboxed — judge submission'ni ham, validatorni ham SHU orqali ishga
// tushiradi. O'zgaruvchi bo'lishining yagona sababi — testlar: bosqichlar
// tartibini (validator submission'dan OLDIN) nsjail'siz tekshirish uchun
// uni soxta ijrochi bilan almashtiradi. Ishlab chiqarishda qayta
// tayinlanmaydi.
var sandboxed sandboxRun = runSandboxed

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

	// Limitlar MAJBURIY. Qo'yib bo'lmasa — ishonchsiz kodni ISHGA TUSHIRMAYMIZ.
	// Avval bu xatolar `_ =` bilan yutilar edi; natijada fork bomb cheklovsiz
	// ishlab, host'ni global OOM ga olib bordi (2026-09-06).
	if lim.Processes > 0 {
		if err := cg.set("pids.max", strconv.Itoa(lim.Processes+4)); err != nil {
			return nil, fmt.Errorf("jarayon limiti qo'yilmadi, ishga tushirilmadi: %w", err)
		}
	} else {
		if err := cg.set("pids.max", "64"); err != nil {
			return nil, fmt.Errorf("jarayon limiti qo'yilmadi, ishga tushirilmadi: %w", err)
		}
	}
	if lim.MemoryKB > 0 {
		if err := cg.set("memory.max", strconv.FormatInt(int64(lim.MemoryKB)*1024, 10)); err != nil {
			return nil, fmt.Errorf("xotira limiti qo'yilmadi, ishga tushirilmadi: %w", err)
		}
	}
	// Swap ni ham yopamiz: aks holda xotira limiti swap'ga siljiydi va
	// host thrashing'ga tushadi (aynan shu narsa ekranni qotirgan).
	if err := cg.set("memory.swap.max", "0"); err != nil {
		return nil, fmt.Errorf("swap limiti qo'yilmadi, ishga tushirilmadi: %w", err)
	}

	wallSec := (wallLimitMs + 999) / 1000
	if wallSec < 1 {
		wallSec = 1
	}
	args := append(nsjailArgs(work, lim, wallSec), "--")
	args = append(args, cmd...)

	// Wall clock uchun qattiq to'xtatgich — nsjail ilinib qolsa ham
	runCtx, cancel := context.WithTimeout(ctx, time.Duration(wallSec+3)*time.Second)
	defer cancel()

	proc := exec.CommandContext(runCtx, "nsjail", args...)

	// Bolani to'g'ridan-to'g'ri o'z cgroup'imizga tug'diramiz (Go 1.22+).
	// Shundagina cpu.stat va memory.peak bizniki bo'ladi.
	if fd, err := os.Open(cg.path); err == nil {
		defer fd.Close()
		proc.SysProcAttr = &syscall.SysProcAttr{
			UseCgroupFD: true,
			CgroupFD:    int(fd.Fd()),
		}
	}

	proc.Stdin = strings.NewReader(stdin)
	var out, errb capBuffer
	out.limit = int64(lim.OutputKB) * 1024
	// Chegaraga yetganda kontekstni bekor qilamiz → CommandContext
	// jarayonni darhol o'ldiradi, wall chegarasi kutilmaydi.
	out.onExceed = cancel
	errb.limit = 64 * 1024
	errb.onExceed = cancel
	proc.Stdout = &out
	proc.Stderr = &errb

	start := time.Now()

	// CPU KUZATUVCHISI.
	// --rlimit_cpu faqat BUTUN soniya qabul qiladi, ya'ni 500 ms limitli
	// masala kamida 1-2 soniya ishlaydi. cgroup cpu.stat ni pollab,
	// chegaraga yetganda darhol to'xtatamiz — aniqlik ~20 ms.
	var watchdogFired atomic.Bool
	if lim.TimeMS > 0 {
		if err := proc.Start(); err != nil {
			return nil, err
		}
		done := make(chan struct{})
		go func() {
			ticker := time.NewTicker(20 * time.Millisecond)
			defer ticker.Stop()
			budget := int64(lim.TimeMS) * 1000 // mikrosoniya
			for {
				select {
				case <-done:
					return
				case <-ticker.C:
					if cg.readInt("cpu.stat", "usage_usec") > budget {
						watchdogFired.Store(true)
						cancel()
						return
					}
				}
			}
		}()
		runErr := proc.Wait()
		close(done)
		wall := time.Since(start).Milliseconds()
		return finishRun(cg, &out, &errb, runErr, wall, wallSec, watchdogFired.Load())
	}

	runErr := proc.Run()
	wall := time.Since(start).Milliseconds()

	return finishRun(cg, &out, &errb, runErr, wall, wallSec, false)
}

func finishRun(cg *cgroup, out, errb *capBuffer, runErr error,
	wall int64, wallSec int, cpuKilled bool) (*runOutcome, error) {

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
		OutputEx: out.Exceeded || errb.Exceeded,
		// CPU kuzatuvchisi to'xtatgan bo'lsa, bu TIMEOUT emas — CPU limiti.
		// classify() cpu_ms ni limitga solishtirib TLE beradi.
		Timeout: !cpuKilled && wall >= int64(wallSec*1000),
	}, nil
}
