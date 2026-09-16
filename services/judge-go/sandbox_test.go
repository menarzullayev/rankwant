package main

import (
	"slices"
	"strings"
	"testing"
)

// Uchdan-uchiga sinovda foydalanuvchiga AYNAN shu qator ko'rindi — hack
// rad etilganda validatorning xabari o'rniga.
const nsjailWarning = "[W][2026-09-16T00:55:49+0000][39] logParams():347 " +
	"Process will be UID/EUID=0 in the global user namespace, and will have " +
	"full access to the directory tree"

func TestStripSandboxLogRemovesWarning(t *testing.T) {
	raw := nsjailWarning + "\nson 1..10^12 oraligida bolishi kerak\n"

	got := stripSandboxLog(raw)

	if got != "son 1..10^12 oraligida bolishi kerak" {
		t.Fatalf("sandbox jurnali kesilmadi: %q", got)
	}
}

func TestStripSandboxLogKeepsFatal(t *testing.T) {
	// Halokatli qator QOLISHI shart: sandbox ishga tushmaganda u yagona
	// tashxis bo'ladi va `IE` bilan operatorga boradi.
	raw := "[F][2026-09-16T00:55:49+0000][39] mkdir('/box'): Permission denied"

	if got := stripSandboxLog(raw); got != raw {
		t.Fatalf("halokatli xabar yo'qoldi: %q", got)
	}
}

func TestStripSandboxLogKeepsCompilerOutput(t *testing.T) {
	// Kompilyator xatosi — eng ko'p ko'riladigan matn. Unda kvadrat
	// qavslar bor (shablon turlari), ya'ni filtr uni tegmasdan o'tkazishi
	// kerak.
	raw := "main.cpp:3:5: error: 'x' was not declared in this scope\n" +
		"    3 | std::vector<int[2]> v;\n      |     ^"

	if got := stripSandboxLog(raw); got != raw {
		t.Fatalf("kompilyator xatosi o'zgardi:\n%q", got)
	}
}

func TestStripSandboxLogEmptyWhenOnlyLog(t *testing.T) {
	if got := stripSandboxLog(nsjailWarning); got != "" {
		t.Fatalf("faqat jurnal bo'lsa bo'sh qolishi kerak: %q", got)
	}
}

// Bayroq sababni yopadi, filtr esa oqibatni. Ikkalasi ham kerak, shuning
// uchun bayroqning O'ZI ham tekshiriladi: `--quiet` ogohlantirishlarni
// yozadi va ular bolaning stderr'iga tushadi.
func TestNsjailArgsSilencesWarnings(t *testing.T) {
	args := nsjailArgs("/tmp/work", Limits{TimeMS: 1000}, 3)

	if !slices.Contains(args, "--really_quiet") {
		t.Fatalf("--really_quiet yo'q: %s", strings.Join(args, " "))
	}
	if slices.Contains(args, "--quiet") {
		t.Fatal("--quiet qaytib kelgan — nsjail ogohlantirishlari yana " +
			"foydalanuvchiga ko'rinadi")
	}
}
