package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"path/filepath"
	"strings"
)

// Kirish validatori — test cheklovlarga mos ekanini tekshiradi (ADR-0020).
//
// ⚠️ Checker'dan MUHIM farqi bor. Checker ham ishonchli dastur, lekin u
// ISHONCHLI ma'lumot ustida ishlaydi — shuning uchun sandboxsiz bajariladi.
// Validator esa ishonchli dastur bo'lsa-da, uning KIRITMASI ishonchsiz: u
// hacker yuborgan test bo'lishi mumkin. Maxsus tanlangan kiritma
// validatorning o'zini cheksiz aylantirib, butun navbatni to'xtatib
// qo'yishi mumkin edi. Shuning uchun u sandbox ICHIDA, chegaralar bilan
// ishlaydi.
//
// Shartnoma (services/bakeoff/protocol.md § «Kirish validatori»):
// kiritma stdin orqali beriladi, chiqish kodi 0 = kiritma to'g'ri, rad
// etish sababi stderr'da.

// Validator chegaralari masalaniki EMAS.
//
// Masala limitlari submission uchun. Ular meros olinsa, 500 ms li
// masalada sekin Python validatori katta kiritmada o'ldirilardi,
// `processes: 1` bilan esa JVM umuman ishga tushmasdi (cgroup `pids.max`
// oqimlarni ham sanaydi — kompilyatsiyaga 64 berilgani bilan bir xil
// sabab). Ikkala holatda ham TO'G'RI kiritma `WRONG_TEST` olardi.
// Validator bizniki, ya'ni kenglik xavf emas; chegara faqat ishonchsiz
// kiritma uni cheksiz cho'zmasligi uchun.
const (
	validatorCompileMS = 30_000
	validatorCPUMS     = 5_000
	validatorWallMS    = 10_000
	validatorMemoryKB  = 1024 * 1024
	validatorOutputKB  = 1_024
	validatorProcesses = 64
	// Rad etish sababi hackerga qaytadi — kiritmani aks ettirgan uzun
	// xabar natijani shishirmasin.
	validatorMessageMax = 1_024
)

func validatorLimits() Limits {
	return Limits{
		TimeMS:    validatorCPUMS,
		MemoryKB:  validatorMemoryKB,
		OutputKB:  validatorOutputKB,
		Processes: validatorProcesses,
	}
}

// validateTests — HAMMA test kirishini submission'ga tegmasdan OLDIN
// tekshiradi.
//
// Qaytaradi: verdict "" — hammasi to'g'ri, judge davom etadi. Aks holda
// `VWrongTest` (kiritma yaroqsiz; birinchi yaroqsiz testning indeksi
// bilan) yoki `VIE` (validator ishlamadi — hacker aybi emas) va izoh.
//
// Nega alohida bosqich va alohida katalog:
//
//   - Submission `/box` ga YOZA oladi. Validator o'sha katalogda testlar
//     orasida ishlasa, 1-testda ishga tushgan submission validator
//     faylini almashtirib, keyingi testlarning tekshiruvini chetlab
//     o'tardi. Shuning uchun hamma kiritma submission kompilyatsiyasidan
//     ham OLDIN tekshiriladi, validator esa o'z katalogida ishlaydi va u
//     bosqich oxirida o'chiriladi — submission uni na o'zgartira, na
//     o'qiy oladi.
//   - Interactive masala o'z tarmog'ida erta qaytadi. Bosqich undan
//     keyin tursa, `validate_input` u yerda jimgina e'tiborsiz qolardi —
//     yopiq yiqilish qoidasining aynan teskarisi.
func validateTests(ctx context.Context, job *Job, tests *store) (string, *int, string) {
	// YOPIQ YIQILISH: bayroq bor, dastur yo'q — ishni RAD ETAMIZ.
	// Tekshiruvsiz davom etish buzuq kiritma bilan istalgan to'g'ri
	// yechimni «sindirish»ga yo'l ochardi.
	if job.Validator == nil {
		return VIE, nil, "validate_input berilgan, lekin validator dasturi yo'q"
	}

	dir, err := os.MkdirTemp("", "rw-validator-*")
	if err != nil {
		return VIE, nil, fmt.Sprintf("validator katalogi yaratilmadi: %v", err)
	}
	defer os.RemoveAll(dir)
	// Jail ichidagi foydalanuvchi (65534) kompilyator natijasini shu yerga
	// yozadi — submission katalogi bilan bir xil huquq.
	if err := os.Chmod(dir, 0o777); err != nil {
		return VIE, nil, fmt.Sprintf("validator katalogi sozlanmadi: %v", err)
	}

	cmd, err := prepareValidator(ctx, dir, job.Validator)
	if err != nil {
		slog.Error("validator tayyorlanmadi", "job", job.JobID, "err", err)
		return VIE, nil, err.Error()
	}
	lim := validatorLimits()
	lim.ProcSelf = job.Validator.ProcSelf
	lim.OpenFiles = job.Validator.OpenFiles

	for i := range job.Tests {
		// Ko'rsatkich orqali: yuklangan ma'lumot job'da qoladi va asosiy
		// tsikl uni S3 dan ikkinchi marta so'ramaydi.
		test := &job.Tests[i]
		if err := resolve(ctx, test, tests); err != nil {
			slog.Error("test ma'lumotini olish", "job", job.JobID, "test", test.Index, "err", err)
			return VIE, nil, fmt.Sprintf("test %d ma'lumoti olinmadi: %v", test.Index, err)
		}
		out, err := sandboxed(ctx, dir, cmd, test.Input, lim, validatorWallMS)
		if err != nil {
			slog.Error("validator ishga tushmadi", "job", job.JobID, "test", test.Index, "err", err)
			return VIE, nil, fmt.Sprintf("validator ishga tushmadi: %v", err)
		}
		if !inputAccepted(out) {
			idx := test.Index
			return VWrongTest, &idx, rejection(out)
		}
	}
	return "", nil, ""
}

// prepareValidator — validator manbasini `dir` ga yozadi va kerak bo'lsa
// kompilyatsiya qiladi. Bosqich boshida BIR MARTA chaqiriladi: har testda
// qayta qurish kompilyatsiya vaqtini test soniga ko'paytirardi.
//
// Checker'dan farqli ravishda kompilyatsiya HAM sandbox ichida, `dir` esa
// `/box` bo'lib ulanadi (`sandbox.go`: `--bindmount work:/box`). Sabab —
// yo'l shartnomasi: validator tili submission tillari jadvalidan keladi va
// uning buyruqlari `/box` ni nazarda tutadi (Java: `javac {src}`, keyin
// `java -cp /box Main`). Fayl nomi ham submission'niki bilan bir xil —
// `Main.java` boshqacha nomlansa javac klassni rad etadi. Ya'ni submission
// uchun ishlaydigan har til validator uchun ham ishlaydi.
func prepareValidator(ctx context.Context, dir string, prog *TrustedProgram) ([]string, error) {
	if len(prog.Run) == 0 {
		return nil, fmt.Errorf("validator ishga tushirish buyrug'i bo'sh")
	}
	src, err := sourceName(prog.Code, prog.SourceFile)
	if err != nil {
		return nil, err
	}
	if err := os.WriteFile(filepath.Join(dir, src), []byte(prog.Source), 0o644); err != nil {
		return nil, fmt.Errorf("validator manbasi yozilmadi: %w", err)
	}

	if len(prog.Compile) > 0 {
		// Kompilyatsiya o'z CPU byudjeti bilan (submission kompilyatsiyasi
		// kabi): testlib bilan -O2 bir necha soniya olishi mumkin.
		lim := validatorLimits()
		lim.TimeMS = validatorCompileMS
		lim.OpenFiles = max(compileOpenFiles, prog.OpenFiles)
		lim.ProcSelf = prog.ProcSelf
		out, err := sandboxed(ctx, dir, subst(prog.Compile, "/box/"+src, "/box/prog"), "",
			lim, validatorCompileMS)
		if err != nil {
			return nil, fmt.Errorf("validator kompilyatsiyasi ishga tushmadi: %w", err)
		}
		if out.Timeout {
			return nil, fmt.Errorf("validator kompilyatsiyasi %d s ichida tugamadi",
				validatorCompileMS/1000)
		}
		if out.ExitCode != 0 {
			return nil, fmt.Errorf("validator kompilyatsiyasi (chiqish kodi %d): %s",
				out.ExitCode, strings.TrimSpace(out.Stderr))
		}
	}
	return subst(prog.Run, "/box/"+src, "/box/prog"), nil
}

// inputAccepted — validator kiritmani qabul qildimi.
//
// Faqat o'z vaqtida va 0 kodi bilan tugash qabul. Vaqt tugashi yoki CPU
// kuzatuvchisining to'xtatishi — rad: aks holda validatorni ataylab
// cho'zadigan kiritma tekshiruvni chetlab o'tardi. Chiqish chegarasidan
// oshish ham rad: jarayon o'rtada o'ldirilayotgan edi, uning «0» i
// ishonchli emas.
func inputAccepted(out *runOutcome) bool {
	return out.ExitCode == 0 && !out.Timeout && !out.OutputEx
}

// rejection — rad etish sababi: validatorning o'z xabari (testlib uni
// stderr'ga yozadi), bo'lmasa chiqish holati.
func rejection(out *runOutcome) string {
	switch {
	case out.Timeout:
		return fmt.Sprintf("validator %d s ichida tugamadi — kiritma rad etildi", validatorWallMS/1000)
	case out.CPUMs >= validatorCPUMS:
		return fmt.Sprintf("validator %d s CPU vaqtida tugamadi — kiritma rad etildi",
			validatorCPUMS/1000)
	case out.OutputEx:
		return "validator chiqish chegarasidan oshdi — kiritma rad etildi"
	}
	msg := strings.TrimSpace(out.Stderr)
	if msg == "" {
		msg = strings.TrimSpace(out.Stdout)
	}
	if msg == "" {
		return fmt.Sprintf("validator kiritmani rad etdi (chiqish kodi %d)", out.ExitCode)
	}
	if len(msg) > validatorMessageMax {
		// Bayt chegarasida kesilgan UTF-8 belgisi JSON'da buzilmasin.
		msg = strings.ToValidUTF8(msg[:validatorMessageMax], "") + "…"
	}
	return msg
}
