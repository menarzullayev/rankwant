package main

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"
	"unicode/utf8"
)

// Validator bosqichining testlari nsjail'siz ishlaydi: `sandboxed` soxta
// ijrochi bilan almashtiriladi va har chaqiruv yozib boriladi. Haqiqiy
// sandbox'dagi xatti-harakat — bake-off `19`–`21` case'larida.

const python = "/usr/bin/python3"

// sandboxCall — soxta ijrochiga kelgan bitta chaqiruv.
type sandboxCall struct {
	dir   string
	cmd   []string
	stdin string
	lim   Limits
	wall  int
}

// validator — chaqiruv validator katalogida bo'ldimi (submission emas).
func (c sandboxCall) validator() bool {
	return strings.HasPrefix(filepath.Base(c.dir), "rw-validator-")
}

// fakeSandbox — test davomida `sandboxed` o'rniga turadi.
func fakeSandbox(t *testing.T, respond func(sandboxCall) (*runOutcome, error)) *[]sandboxCall {
	t.Helper()
	calls := &[]sandboxCall{}
	prev := sandboxed
	sandboxed = func(_ context.Context, work string, cmd []string, stdin string,
		lim Limits, wallLimitMs int) (*runOutcome, error) {
		c := sandboxCall{dir: work, cmd: slices.Clone(cmd), stdin: stdin, lim: lim, wall: wallLimitMs}
		*calls = append(*calls, c)
		return respond(c)
	}
	t.Cleanup(func() { sandboxed = prev })
	return calls
}

func partition(calls []sandboxCall) (validator, submission []sandboxCall) {
	for _, c := range calls {
		if c.validator() {
			validator = append(validator, c)
		} else {
			submission = append(submission, c)
		}
	}
	return validator, submission
}

func pyProgram(source string) *TrustedProgram {
	return &TrustedProgram{Code: "py312", Run: []string{python, "{src}"}, Source: source}
}

// validatedJob — masala limitlari ATAYLAB tor: validator ularni meros
// olmasligini tekshirish uchun.
func validatedJob(inputs ...string) *Job {
	job := &Job{
		JobID:    "validator-test",
		Language: Language{Code: "py312", Run: []string{python, "{src}"}},
		Source:   "a, b = map(int, input().split())\nprint(a + b)\n",
		Limits: Limits{CompileTimeMS: 10_000, TimeMS: 500, MemoryKB: 16_384,
			OutputKB: 1_024, Processes: 1},
		Checker:       Checker{Type: "standard"},
		Mode:          "acm",
		Validator:     pyProgram("import sys\n"),
		ValidateInput: true,
	}
	for i, in := range inputs {
		job.Tests = append(job.Tests, Test{Index: i + 1, Input: in, Expected: "3\n"})
	}
	return job
}

// rejectsZero — soxta validator "0" bilan boshlangan kiritmani rad etadi;
// submission har doim to'g'ri javob beradi.
func rejectsZero(c sandboxCall) (*runOutcome, error) {
	if !c.validator() {
		return &runOutcome{Stdout: "3\n"}, nil
	}
	if strings.HasPrefix(c.stdin, "0") {
		return &runOutcome{ExitCode: 3, Stderr: "1 <= a buzildi: a=0\n"}, nil
	}
	return &runOutcome{}, nil
}

func TestPrepareValidatorInterpretedRunsFromBox(t *testing.T) {
	calls := fakeSandbox(t, func(sandboxCall) (*runOutcome, error) {
		return nil, errors.New("interpretatsiya qilinadigan validator kompilyatsiya qilinmaydi")
	})
	dir := t.TempDir()

	cmd, err := prepareValidator(context.Background(), dir, pyProgram("import sys\n"))
	if err != nil {
		t.Fatal(err)
	}
	if want := []string{python, "/box/main.py"}; !slices.Equal(cmd, want) {
		t.Fatalf("buyruq %q, kutilgan %q — validator /box ichidan ishlashi shart", cmd, want)
	}
	got, err := os.ReadFile(filepath.Join(dir, "main.py"))
	if err != nil || string(got) != "import sys\n" {
		t.Fatalf("manba yozilmadi: %q, %v", got, err)
	}
	if len(*calls) != 0 {
		t.Fatalf("sandbox %d marta chaqirildi, 0 kutilgan", len(*calls))
	}
}

func TestPrepareValidatorCompilesInsideBox(t *testing.T) {
	calls := fakeSandbox(t, func(sandboxCall) (*runOutcome, error) { return &runOutcome{}, nil })
	dir := t.TempDir()
	prog := &TrustedProgram{
		Code:    "java21",
		Compile: []string{"/usr/bin/javac", "{src}"},
		Run:     []string{"/usr/bin/java", "-cp", "/box", "Main"},
		Source:  "public class Main { public static void main(String[] a) {} }\n",
	}

	cmd, err := prepareValidator(context.Background(), dir, prog)
	if err != nil {
		t.Fatal(err)
	}
	if len(*calls) != 1 {
		t.Fatalf("kompilyatsiya %d marta chaqirildi, 1 kutilgan", len(*calls))
	}
	compile := (*calls)[0]
	// Submission bilan bir xil yo'l shartnomasi: aks holda javac /box
	// ichidagi faylni topmaydi yoki klass nomi fayl nomiga mos kelmaydi.
	if want := []string{"/usr/bin/javac", "/box/Main.java"}; !slices.Equal(compile.cmd, want) {
		t.Fatalf("kompilyatsiya buyrug'i %q, kutilgan %q", compile.cmd, want)
	}
	if compile.dir != dir {
		t.Fatalf("kompilyatsiya %q da, validator katalogi %q", compile.dir, dir)
	}
	if compile.lim.Processes != validatorProcesses || compile.lim.MemoryKB != validatorMemoryKB {
		t.Fatalf("kompilyatsiya limitlari %+v — JVM uchun yetmaydi", compile.lim)
	}
	if want := []string{"/usr/bin/java", "-cp", "/box", "Main"}; !slices.Equal(cmd, want) {
		t.Fatalf("ishga tushirish %q, kutilgan %q", cmd, want)
	}
	if _, err := os.Stat(filepath.Join(dir, "Main.java")); err != nil {
		t.Fatalf("Main.java yozilmadi: %v", err)
	}
}

func TestPrepareValidatorCompileFailure(t *testing.T) {
	for name, out := range map[string]*runOutcome{
		"xato":        {ExitCode: 1, Stderr: "main.cpp:1: expected ';'"},
		"vaqt tugadi": {Timeout: true},
	} {
		t.Run(name, func(t *testing.T) {
			fakeSandbox(t, func(sandboxCall) (*runOutcome, error) { return out, nil })
			prog := &TrustedProgram{Code: "cpp23", Run: []string{"{bin}"}, Source: "int main( {}\n",
				Compile: []string{"/usr/bin/g++", "-o", "{bin}", "{src}"}}
			_, err := prepareValidator(context.Background(), t.TempDir(), prog)
			if err == nil || !strings.Contains(err.Error(), "validator kompilyatsiyasi") {
				t.Fatalf("kompilyatsiya xatosi qaytmadi: %v", err)
			}
		})
	}
}

func TestPrepareValidatorEmptyRun(t *testing.T) {
	fakeSandbox(t, rejectsZero)
	if _, err := prepareValidator(context.Background(), t.TempDir(), &TrustedProgram{Code: "py312"}); err == nil {
		t.Fatal("bo'sh ishga tushirish buyrug'i xato bermadi")
	}
}

func TestInputAccepted(t *testing.T) {
	for _, tc := range []struct {
		name string
		out  runOutcome
		want bool
	}{
		{"0 kodi", runOutcome{}, true},
		{"cheklov buzilgan", runOutcome{ExitCode: 3}, false},
		{"o'ldirilgan", runOutcome{ExitCode: -1}, false},
		// Validatorni cho'zgan kiritma tekshiruvdan o'tib ketmasin.
		{"vaqt tugadi, kod 0", runOutcome{Timeout: true}, false},
		{"chiqish chegarasi, kod 0", runOutcome{OutputEx: true}, false},
	} {
		if got := inputAccepted(&tc.out); got != tc.want {
			t.Errorf("%s: %v, kutilgan %v", tc.name, got, tc.want)
		}
	}
}

func TestRejectionMessage(t *testing.T) {
	if got := rejection(&runOutcome{ExitCode: 3, Stderr: "  1 <= n buzildi\n"}); got != "1 <= n buzildi" {
		t.Errorf("stderr xabari: %q", got)
	}
	if got := rejection(&runOutcome{ExitCode: 2}); !strings.Contains(got, "chiqish kodi 2") {
		t.Errorf("xabarsiz rad etish: %q", got)
	}
	if got := rejection(&runOutcome{Timeout: true}); !strings.Contains(got, "tugamadi") {
		t.Errorf("vaqt tugashi: %q", got)
	}
	if got := rejection(&runOutcome{ExitCode: -1, CPUMs: validatorCPUMS + 20}); !strings.Contains(got, "CPU") {
		t.Errorf("CPU kuzatuvchisi: %q", got)
	}
	// Bitta ASCII belgi siljitadi: kesish ikki baytli belgining o'rtasiga tushadi.
	long := rejection(&runOutcome{ExitCode: 1, Stderr: "a" + strings.Repeat("ж", validatorMessageMax)})
	if len(long) > validatorMessageMax+len("…") || !utf8.ValidString(long) {
		t.Errorf("uzun xabar kesilmadi yoki UTF-8 buzildi: %d bayt", len(long))
	}
}

func TestJudgeValidatesEveryInputBeforeSubmission(t *testing.T) {
	calls := fakeSandbox(t, rejectsZero)

	res := judge(context.Background(), validatedJob("1 2\n", "0 3\n", "1 2\n"), nil)

	if res.Verdict != VWrongTest {
		t.Fatalf("verdict %s, kutilgan %s", res.Verdict, VWrongTest)
	}
	if res.FailedTestIndex == nil || *res.FailedTestIndex != 2 {
		t.Fatalf("failed_test_index %v, kutilgan 2", res.FailedTestIndex)
	}
	if !strings.Contains(res.CompileOutput, "1 <= a buzildi") {
		t.Fatalf("rad etish sababi qaytmadi: %q", res.CompileOutput)
	}
	validator, submission := partition(*calls)
	// Birinchi test TO'G'RI bo'lsa ham submission ishga tushmaydi: tekshiruv
	// testlar orasida bo'lsa, u 1-testda validator faylini almashtira olardi.
	if len(submission) != 0 || len(res.PerTest) != 0 {
		t.Fatalf("submission %d marta ishga tushdi — validatsiya undan OLDIN tugashi shart",
			len(submission))
	}
	if len(validator) != 2 || validator[0].stdin != "1 2\n" || validator[1].stdin != "0 3\n" {
		t.Fatalf("validator chaqiruvlari %+v — birinchi yaroqsiz testda to'xtashi kerak", validator)
	}
	for _, c := range validator {
		if c.lim != validatorLimits() || c.wall != validatorWallMS {
			t.Fatalf("validator limitlari %+v, wall %d — masalaning tor limitlari meros olingan",
				c.lim, c.wall)
		}
	}
	if _, err := os.Stat(validator[0].dir); !os.IsNotExist(err) {
		t.Fatalf("validator katalogi o'chirilmadi (%v) — submission uni ko'ra olardi", err)
	}
}

func TestJudgeValidInputsReachSubmission(t *testing.T) {
	calls := fakeSandbox(t, rejectsZero)

	res := judge(context.Background(), validatedJob("1 2\n", "1 2\n"), nil)

	if res.Verdict != VAC {
		t.Fatalf("verdict %s, kutilgan AC: %s", res.Verdict, res.CompileOutput)
	}
	lastValidator, firstSubmission := -1, -1
	for i, c := range *calls {
		if c.validator() {
			lastValidator = i
		} else if firstSubmission < 0 {
			firstSubmission = i
		}
	}
	if lastValidator != 1 || firstSubmission != 2 {
		t.Fatalf("tartib buzilgan: oxirgi validator #%d, birinchi submission #%d",
			lastValidator, firstSubmission)
	}
	if _, submission := partition(*calls); len(submission) != 2 {
		t.Fatalf("submission %d marta ishga tushdi, 2 kutilgan", len(submission))
	}
}

func TestJudgeFailsClosedWithoutValidator(t *testing.T) {
	calls := fakeSandbox(t, rejectsZero)
	job := validatedJob("1 2\n")
	job.Validator = nil

	res := judge(context.Background(), job, nil)

	if res.Verdict != VIE || !strings.Contains(res.CompileOutput, "validator") {
		t.Fatalf("verdict %s (%q) — bayroq bor, dastur yo'q: IE kutilgan", res.Verdict, res.CompileOutput)
	}
	if len(*calls) != 0 {
		t.Fatalf("sandbox %d marta chaqirildi — ish tekshiruvsiz davom etdi", len(*calls))
	}
}

func TestJudgeValidatesInteractiveInputs(t *testing.T) {
	calls := fakeSandbox(t, rejectsZero)
	job := validatedJob("0 7\n")
	job.Checker = Checker{Type: "interactive", Interactor: pyProgram("import sys\n")}

	res := judge(context.Background(), job, nil)

	// Interactive tarmoq erta qaytadi: bosqich undan keyin tursa, bayroq
	// jimgina e'tiborsiz qolardi.
	if res.Verdict != VWrongTest {
		t.Fatalf("verdict %s — interactive masalada validatsiya o'tkazib yuborildi", res.Verdict)
	}
	if _, submission := partition(*calls); len(submission) != 0 {
		t.Fatalf("submission %d marta ishga tushdi", len(submission))
	}
}

func TestJudgeSkipsValidatorWhenNotRequested(t *testing.T) {
	calls := fakeSandbox(t, rejectsZero)
	job := validatedJob("0 3\n")
	job.ValidateInput = false

	res := judge(context.Background(), job, nil)

	// Masalaning o'z testlari muallifniki — ularni har yuborishda qayta
	// tekshirish isrof.
	if validator, _ := partition(*calls); len(validator) != 0 {
		t.Fatalf("validator %d marta chaqirildi — bayroqsiz ishda validatsiya yo'q", len(validator))
	}
	if res.Verdict != VAC {
		t.Fatalf("verdict %s, kutilgan AC", res.Verdict)
	}
}

func TestJudgeValidatorInfrastructureErrorIsIE(t *testing.T) {
	calls := fakeSandbox(t, func(c sandboxCall) (*runOutcome, error) {
		if c.validator() {
			return nil, errors.New("cgroup yaratilmadi")
		}
		return &runOutcome{Stdout: "3\n"}, nil
	})

	res := judge(context.Background(), validatedJob("1 2\n"), nil)

	// Validator ishlamagani hacker aybi emas: WRONG_TEST uning testini
	// nohaq «yaroqsiz» deb belgilardi.
	if res.Verdict != VIE || res.FailedTestIndex != nil {
		t.Fatalf("verdict %s, failed %v — IE kutilgan", res.Verdict, res.FailedTestIndex)
	}
	if _, submission := partition(*calls); len(submission) != 0 {
		t.Fatalf("submission %d marta ishga tushdi", len(submission))
	}
}
