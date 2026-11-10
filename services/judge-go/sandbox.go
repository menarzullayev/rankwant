package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
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

	// O'ldirilish SABABI. Verdict shu ikkisiga tayanadi, lekin ilgari ular
	// jurnalga chiqmasdi: 2026-09-17 da `04-idleness` CI'da `IDLENESS`
	// o'rniga `RE_SIGNAL` berdi (total 2003 ms, CPU ~0) va sabab
	// ko'rinmadi. Taxmin qilish o'rniga o'lchangan qiymat yoziladi.
	CPUKilled  bool
	WallKilled bool
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
	// Ota darajasidagi shift — ikkinchi himoya qatlami. ADR-0046 rejimida
	// (JUDGE_USERNS=1) uni root `setupDelegatedCgroup` da yozadi va fayllar
	// root'niki qoladi: bu yozuvlar EACCES bilan jim o'tadi — ataylab,
	// worker o'z shiftini ko'tara olmasligi kerak.
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

// PreflightSandbox runs one real program through nsjail before the worker
// takes a job. The cgroup preflight proves limits can be set; this proves a
// program can start at all. Without it a container option lost in a compose
// edit (measured 2026-11-10: without `systempaths=unconfined` nsjail cannot
// remount its chroot) left the worker up and every submission CE.
//
// It also reads the sandbox's uid map: with the launcher on (ADR-0046) the
// program must not be uid 0 outside its namespace.
func PreflightSandbox(ctx context.Context) error {
	work, err := os.MkdirTemp("", "rw-preflight-*")
	if err != nil {
		return err
	}
	defer os.RemoveAll(work)
	if err := os.Chmod(work, 0o777); err != nil {
		return err
	}
	lim := Limits{TimeMS: 2000, MemoryKB: 131072, OutputKB: 64, Processes: 1, ProcSelf: true}
	out, err := sandboxed(ctx, work, []string{"/bin/cat", "/proc/self/uid_map"}, "", lim, 10000)
	if err != nil {
		return fmt.Errorf("sandbox ishga tushmadi: %w", err)
	}
	if out.ExitCode != 0 {
		return fmt.Errorf("sandbox ishlamadi: exit %d: %s", out.ExitCode, strings.TrimSpace(out.Stderr))
	}
	return checkUIDMap(out.Stdout, usernsEnabled())
}

// checkUIDMap reads `inside outside count` from the sandbox's uid_map.
func checkUIDMap(uidMap string, rootless bool) error {
	fields := strings.Fields(uidMap)
	if len(fields) != 3 || fields[0] != "65534" {
		return fmt.Errorf("sandbox uid_map kutilmagan: %q", strings.TrimSpace(uidMap))
	}
	if rootless && fields[1] == "0" {
		return errors.New("sandbox tashqarida uid 0 — ADR-0046 buzilgan")
	}
	return nil
}

// sandboxLogLine — nsjail'ning O'Z jurnal qatori:
// `[W][2026-09-16T00:55:49+0000][39] logParams():347 …`.
var sandboxLogLine = regexp.MustCompile(`^\[([IWDEF])\]\[[^\]]*\]\[\d+\] `)

// stripSandboxLog — sandbox jurnalini foydalanuvchiga boradigan matndan
// olib tashlaydi.
//
// Bayroq (`--really_quiet`) sababni yopadi, bu esa OQIBATNI: nsjail
// versiyasi almashsa yoki kimdir bayroqni qaytarsa, jurnal yana
// kompilyatsiya xatosi va validator sababi bilan aralashib ketardi.
// Ikkalasi ham arzon, matn esa foydalanuvchiga ko'rinadi.
//
// `[E]` va `[F]` QOLDIRILADI: sandbox ishga tusha olmaganda o'sha qator
// yagona tashxis bo'ladi va u `IE` bilan operatorga boradi.
func stripSandboxLog(s string) string {
	if !strings.Contains(s, "][") {
		return s
	}
	lines := strings.Split(s, "\n")
	kept := make([]string, 0, len(lines))
	for _, line := range lines {
		if m := sandboxLogLine.FindStringSubmatch(line); m != nil && m[1] != "E" && m[1] != "F" {
			continue
		}
		kept = append(kept, line)
	}
	return strings.TrimSpace(strings.Join(kept, "\n"))
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

// nsjailBackstopSec keeps nsjail's own --time_limit far behind the wall limit.
//
// nsjail checks that limit against time(NULL): whole seconds of the REALTIME
// clock. On this host the realtime clock of the WSL2 VM, shared by the CI
// engine and Docker Desktop, is stepped every ~30 s (systemd-timesyncd in the
// Ubuntu distro against Hyper-V time sync; measured 2026-09-17: 226 clock
// changes in an hour, offset +1.34 s, steps of +2 s inside a container). With
// --time_limit equal to the wall limit, nsjail killed `time.sleep(10)` after
// 1002 ms and 2003 ms of real time, before the watcher below, so 04-idleness
// came back as RE_SIGNAL instead of IDLENESS (judge log: exit=137,
// wall_killed=false; clock changes at 23:46:33.8 and 23:46:35.3 UTC around the
// kill at 23:46:35).
//
// The wall limit is enforced on the monotonic clock instead: by the watcher and
// runCtx in runSandboxed, and by the caller's context in the interactive path.
// nsjail's limit only reaps a sandbox whose judge has died.
const nsjailBackstopSec = 30

// sandboxSeccomp — kafel policy for the sandboxed program (nsjail applies
// it right before exec; nsjail's own setup is not under it). EPERM, not
// KILL: Docker's default profile answers these the same way, so a runtime
// that probes them (glibc's clone3) behaves as it does in any container.
// 0x7e020000 is every CLONE_NEW* flag (the mask Docker's profile uses).
// In kafel's syscall table `umount` is umount2 (nr 166; checked by errno).
const sandboxSeccomp = "ERRNO(1) { mount, umount, pivot_root, sethostname, unshare, setns, " +
	"clone { (clone_flags & 0x7e020000) != 0 } }, ERRNO(38) { clone3 } DEFAULT ALLOW"

// nsjailArgs — izolyatsiya konfiguratsiyasi.
// Har bir bayroq bake-off case'iga javob beradi (services/bakeoff/cases/).
func nsjailArgs(work string, lim Limits, wallSec int) []string {
	args := []string{
		// `--quiet` EMAS: u ogohlantirishlarni ham yozadi va nsjail ularni
		// BOLANING stderr'iga chiqaradi, ya'ni ular kompilyatsiya xatosi
		// bilan bir oqimda foydalanuvchiga borardi. O'lchandi (uchdan-uchiga
		// sinov): hack rad etilganda sabab sifatida validatorning xabari
		// emas, «[W][…] logParams():347 Process will be UID/EUID=0 in the
		// global user namespace…» ko'rindi. `--really_quiet` faqat halokatli
		// xabarlarni qoldiradi — sandbox umuman ishga tushmasa, o'sha qator
		// yagona tashxis bo'lgani uchun u KERAK.
		"--really_quiet",
		"--mode", "o", // bir marta ishga tushir va chiq
		// Host ildizi READ-ONLY ko'rinadi — kompilyator va kutubxonalar kerak,
		// lekin yozib bo'lmaydi (10-file-write). Yoziladigan yagona joy — /box.
		"--chroot", "/",
		"--bindmount", work + ":/box",
		"--cwd", "/box",
		// inside=65534, outside = nsjail'ni ishga tushirgan uid.
		// ADR-0046 (2026-11-10): worker judge foydalanuvchisi (10001) bo'lib
		// ishlaydi, ya'ni yechim tashqarida uid 10001 — ilgari 0 edi.
		// Ilgarigi «mkdir(...): Permission denied» (nsjail mount nuqtasini
		// root'niki bo'lgan / ichida yarata olmasdi) image'da `/box` oldindan
		// yaratilgani bilan yopildi (Dockerfile).
		// Qolgan qatlamlar: chroot / READ-ONLY, yoziladigan yagona joy /box,
		// tarmoq yo'q, /proc yo'q, cgroup chegaralari.
		"--user", "65534",
		"--group", "65534",
		"--hostname", "judge",
		// Jail ichida muhit o'zgaruvchilari BO'SH bo'ladi. PATH bo'lmasa g++
		// ishga tushadi, lekin collect2 'ld' ni topa olmay "cannot find 'ld'"
		// beradi — kompilyatsiya CE bo'lib ko'rinadi, aslida sabab boshqa.
		"--env", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
		"--env", "HOME=/box",
		"--env", "LANG=C.UTF-8",
		// ADR-0046: the container's seccomp profile opens six syscalls so
		// that nsjail can build its namespaces (services/judge-go/
		// seccomp.json). The sandboxed program gets them closed again, as
		// Docker's default profile closes them: no mounts, no new namespaces
		// (no user namespace to escalate from), clone3 answered ENOSYS so
		// glibc falls back to clone, whose flags this filter can see.
		// Measured 2026-11-10: without it a program created a user namespace
		// with clone(CLONE_NEWUSER) (bake-off 33-nested-userns).
		"--seccomp_string", sandboxSeccomp,
		// 12-proc-read: --disable_proc faqat YANGI procfs mount'ini to'sadi.
		// --chroot / bo'lgani uchun HOST /proc jail ichiga kirib keladi va
		// /proc/1/cmdline o'qiladi. Ustiga bo'sh tmpfs qo'yib niqoblaymiz.
		"--disable_proc",
	}
	if lim.ProcSelf {
		// 22-proc-self: a fresh procfs in the sandbox's own PID namespace.
		// `subset=pid` drops everything that is not a process directory
		// (meminfo, sys, kallsyms …) and `hidepid=invisible` hides processes
		// of other users, so only the sandbox's own processes are listed.
		args = append(args, "--mount", "none:/proc:proc:subset=pid,hidepid=invisible")
	} else {
		args = append(args, "--tmpfsmount", "/proc")
	}
	openFiles := lim.OpenFiles
	if openFiles <= 0 {
		openFiles = 64
	}
	args = append(args,
		"--iface_no_lo",        // 11-network: tarmoq interfeysi yo'q
		"--rlimit_fsize", "16", // MB — sandbox ichida ham fayl cheklovi
		"--rlimit_nofile", strconv.Itoa(openFiles),
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
		"--time_limit", strconv.Itoa(wallSec+nsjailBackstopSec), // backstop only, see nsjailBackstopSec
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
	)
	// 09-fork-bomb: the process limit is the run cgroup's `pids.max`
	// (applyLimits / runSandboxed), and nothing else. There is deliberately
	// no `--rlimit_nproc`:
	//
	//  - Under `privileged` it never applied. The sandbox ran as host uid 0
	//    and the kernel does not hold uid 0 to RLIMIT_NPROC, so `pids.max`
	//    stopped every fork bomb in production.
	//  - Applied for the first time, as uid 10001 (ADR-0046), it made each
	//    failed fork cheap: the bomb retried far faster, the task structs
	//    of the failed forks waited for RCU, and that kernel memory, charged
	//    to the run, hit `memory.max`. 09-fork-bomb came back MLE in 7 runs
	//    of 8 (peak 262144 kB, `task_struct` slab +177 MB); without the flag
	//    TLE in 6 of 6 at 95-139 MB, as under `privileged` (8 of 8, 90-118
	//    MB). Measured 2026-11-10.
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

	if err := proc.Start(); err != nil {
		return nil, err
	}
	done := make(chan struct{})

	// CPU KUZATUVCHISI.
	// --rlimit_cpu faqat BUTUN soniya qabul qiladi, ya'ni 500 ms limitli
	// masala kamida 1-2 soniya ishlaydi. cgroup cpu.stat ni pollab,
	// chegaraga yetganda darhol to'xtatamiz — aniqlik ~20 ms.
	var cpuFired atomic.Bool
	if lim.TimeMS > 0 {
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
						cpuFired.Store(true)
						cancel()
						return
					}
				}
			}
		}()
	}

	// WALL KUZATUVCHISI.
	//
	// Ilgari wall chegarasini faqat nsjail'ning `--time_limit` i ushlardi
	// va verdict SABABI o'lchangan vaqtga qarab TAXMIN qilinardi:
	// `wall >= wallSec*1000`. Bu poyga edi, chunki ikki soat har xil
	// nuqtadan boshlanadi: bizning `start` — nsjail ishga tushishidan
	// OLDIN, nsjail'ning taymeri esa bola exec bo'lgandan KEYIN.
	//
	// O'lchandi (2026-09-16): bo'sh mashinada farq ~3 ms
	// (`total_ms = 3003`, chegara 3000) — ya'ni o'tish tasodifga bog'liq.
	// CI'da (ikki job bitta runner'da, to'liq stack) nsjail'ning
	// tayyorlanishi ~1 s cho'zilgan va o'lchangan wall **2003** chiqqan:
	// `2003 >= 3000` → false → verdict IDLENESS o'rniga **RE_SIGNAL**.
	// Aynan shu `04-idleness` ni bir marta yiqitgan.
	//
	// Endi to'xtatish SABABI o'lchanadi: taymer `start` dan emas, balki
	// `proc.Start()` dan keyin darhol qo'yiladi va chegaraga yetganda
	// o'zimiz o'ldiramiz. `--time_limit` (yuqoriga yaxlitlangan soniya)
	// zaxira bo'lib qoladi.
	var wallFired atomic.Bool
	go func() {
		timer := time.NewTimer(time.Duration(wallLimitMs) * time.Millisecond)
		defer timer.Stop()
		select {
		case <-done:
			return
		case <-timer.C:
			wallFired.Store(true)
			cancel()
		}
	}()

	runErr := proc.Wait()
	close(done)
	wall := time.Since(start).Milliseconds()

	return finishRun(cg, &out, &errb, runErr, wall, wallSec, cpuFired.Load(), wallFired.Load())
}

func finishRun(cg *cgroup, out, errb *capBuffer, runErr error,
	wall int64, wallSec int, cpuKilled, wallKilled bool) (*runOutcome, error) {

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
		Stdout: out.String(),
		// Sandbox jurnali shu yerda kesiladi — barcha iste'molchilar
		// (kompilyatsiya chiqishi, validator sababi) toza matn oladi.
		Stderr:   stripSandboxLog(errb.String()),
		ExitCode: exit,
		CPUMs:    cpuUsec / 1000,
		WallMs:   wall,
		PeakKB:   peak / 1024,
		OOMKill:  oom,
		OutputEx: out.Exceeded || errb.Exceeded,
		// CPU kuzatuvchisi to'xtatgan bo'lsa, bu TIMEOUT emas — CPU limiti.
		// classify() cpu_ms ni limitga solishtirib TLE beradi.
		Timeout:    wallTimedOut(cpuKilled, wallKilled, wall, wallSec),
		CPUKilled:  cpuKilled,
		WallKilled: wallKilled,
	}, nil
}

// wallTimedOut — jarayonni WALL chegarasi to'xtatganini aytadi.
//
// Ikki manba: bizning wall kuzatuvchimiz (`wallKilled`) va nsjail'ning
// `--time_limit` i (zaxira — o'lchangan vaqt bo'yicha taxmin).
//
// ⚠️ CPU kuzatuvchisi ishlagan bo'lsa bu TIMEOUT EMAS: u TLE yoki
// IDLENESS, va `classify` buni `cpu_ms` bo'yicha o'zi ajratadi. Aks holda
// CPU limitida o'lgan yechim «IDLENESS» bo'lib ko'rinardi.
//
// ⚠️ Taxminiy shox (`wall >= wallSec*1000`) ATAYLAB qoldirilgan: u
// nsjail o'zi o'ldirgan holat uchun zaxira, lekin unga TAYANIB
// BO'LMAYDI — `wallSec` yuqoriga yaxlitlanadi, o'lchov esa nsjail
// tayyorlanishini qamramaydi (o'lchandi: farq 3 ms dan ~1 s gacha).
func wallTimedOut(cpuKilled, wallKilled bool, wall int64, wallSec int) bool {
	if cpuKilled {
		return false
	}
	return wallKilled || wall >= int64(wallSec*1000)
}
