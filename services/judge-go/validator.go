package main

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"
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
// kiritma stdin orqali beriladi, chiqish kodi 0 = kiritma to'g'ri.
const validatorWallMS = 5_000

// prepareValidator — validator manbasini `work` ga yozadi va kerak bo'lsa
// kompilyatsiya qiladi. Job boshida BIR MARTA chaqiriladi: har testda qayta
// qurish kompilyatsiya vaqtini test soniga ko'paytirardi (`prepareChecker`
// bilan bir xil sabab).
//
// Kompilyatsiya sandbox TASHQARISIDA bo'ladi — manba bizniki, ishonchli.
// Ishga tushirish esa ICHIDA, shuning uchun qaytariladigan buyruq `/box/`
// yo'llarida bo'ladi: `work` katalogi sandbox ichida aynan `/box` bo'lib
// ko'rinadi (`sandbox.go`: `--bindmount work:/box`).
func prepareValidator(ctx context.Context, work string, prog *TrustedProgram) ([]string, error) {
	name := "validator_" + srcName(prog.Code)
	hostSrc := filepath.Join(work, name)
	if err := os.WriteFile(hostSrc, []byte(prog.Source), 0o644); err != nil {
		return nil, err
	}

	if len(prog.Compile) > 0 {
		cctx, cancel := context.WithTimeout(ctx, 30*time.Second)
		defer cancel()
		cmd := subst(prog.Compile, hostSrc, filepath.Join(work, "validator_bin"))
		out, err := exec.CommandContext(cctx, cmd[0], cmd[1:]...).CombinedOutput()
		if err != nil {
			return nil, fmt.Errorf("validator kompilyatsiyasi: %w: %s", err, string(out))
		}
	}

	// Ishga tushirish buyrug'i sandbox ichidagi yo'llar bilan.
	return subst(prog.Run, "/box/"+name, "/box/validator_bin"), nil
}

// validateInput — bitta test kirishini tekshiradi.
//
// `true` — kiritma cheklovlarga mos. `false` — mos emas yoki validator uni
// belgilangan vaqtda baholay olmadi.
func validateInput(ctx context.Context, work string, runCmd []string,
	input string, lim Limits) (bool, error) {

	// Validator o'z chegaralarida ishlaydi, masala limitlarida emas: u
	// bizniki va yengil, lekin ishonchsiz kiritma uni cho'zishi mumkin.
	vl := lim
	vl.Processes = 1

	out, err := runSandboxed(ctx, work, runCmd, input, vl, validatorWallMS)
	if err != nil {
		return false, err
	}

	// Vaqt tugadi — kiritmani to'g'ri deb hisoblab BO'LMAYDI. Aks holda
	// validatorni ataylab cho'zadigan kiritma tekshiruvni chetlab o'tardi.
	if out.Timeout {
		return false, nil
	}

	return out.ExitCode == 0, nil
}
