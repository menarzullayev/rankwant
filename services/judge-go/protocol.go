package main

// Shartnoma: services/bakeoff/protocol.md
// Bu tuzilmalar judge-py bilan BIR XIL bo'lishi shart — nomzodlar almashtiriladigan.

type Language struct {
	Code string `json:"code"`
	// SourceFile is the name the source is saved under (main.kt, Main.java).
	// Compilers pick the language from the extension and JVM languages want
	// the class name in it. Empty keeps the old code-prefix mapping, which the
	// bake-off cases still rely on.
	SourceFile string   `json:"source_file,omitempty"`
	Compile    []string `json:"compile"`
	Run        []string `json:"run"`
	// ProcSelf mounts a procfs that shows only the sandbox's own processes
	// (a new PID namespace, `subset=pid`) instead of masking /proc with an
	// empty tmpfs. Runtimes that locate themselves through /proc/self/exe or
	// read their stack bounds from /proc/self/maps — CoreCLR, Dart, Julia,
	// the Swift compiler — cannot start under the mask. Host
	// processes stay invisible either way (bake-off `22-proc-self`).
	ProcSelf bool `json:"proc_self,omitempty"`
	// OpenFiles is RLIMIT_NOFILE for this language's programs; 0 keeps the
	// default 64. R refuses to start below ~192 and PowerShell cannot load
	// its assemblies (measured: 128 fails, 192 works).
	OpenFiles int `json:"open_files,omitempty"`
}

type Limits struct {
	CompileTimeMS int `json:"compile_time_ms"`
	TimeMS        int `json:"time_ms"`
	MemoryKB      int `json:"memory_kb"`
	OutputKB      int `json:"output_kb"`
	Processes     int `json:"processes"`

	// Set by the judge for one sandbox run from the language; never part of
	// a job's limits. See Language.OpenFiles and Language.ProcSelf.
	OpenFiles int  `json:"-"`
	ProcSelf  bool `json:"-"`
}

type Test struct {
	Index    int    `json:"index"`
	Input    string `json:"input"`
	Expected string `json:"expected"`
	// API test ma'lumotini emas, S3 havolasini yuboradi (08-technical-spec).
	// Inline maydonlar bake-off harness'i uchun qoladi.
	InputRef    string `json:"input_ref"`
	ExpectedRef string `json:"output_ref"`
	// IOI ballash: test qaysi guruhga tegishli (0 = guruhsiz) va `sum`
	// ballashda shu testning o'z bali.
	Subtask int `json:"subtask,omitempty"`
	Points  int `json:"points,omitempty"`
}

// Subtask — IOI ballash guruhi.
//
//	min: guruh TO'LIQ o'tsagina ball beriladi (odatiy IOI)
//	sum: har test o'z balini olib keladi
type Subtask struct {
	ID      int    `json:"id"`
	Points  int    `json:"points"`
	Scoring string `json:"scoring"`
}

// TrustedProgram — masala bilan keladigan ishonchli dastur:
// interactor, checker yoki validator.
//
// ⚠️ Ular BIR XIL joyda ishlamaydi. Interactor va checker sandbox
// TASHQARISIDA bajariladi: dastur ham, unga beriladigan ma'lumot ham
// bizniki. Validator esa ISHONCHSIZ kiritma ustida ishlaydi (hacker
// yuborgan test), shuning uchun u sandbox ICHIDA bajarilishi shart —
// aks holda buzuq kiritma validatorning o'zini cheksiz aylantirib,
// butun navbatni to'xtatib qo'yardi.
type TrustedProgram struct {
	Code string `json:"code"`
	// SourceFile — see Language.SourceFile.
	SourceFile string   `json:"source_file,omitempty"`
	Compile    []string `json:"compile"`
	Run        []string `json:"run"`
	Source     string   `json:"source"`
	// ProcSelf and OpenFiles — see Language. Only the validator runs in the
	// sandbox; checkers and interactors ignore both.
	ProcSelf  bool `json:"proc_self,omitempty"`
	OpenFiles int  `json:"open_files,omitempty"`
}

type Checker struct {
	// standard | interactive | scorer
	//
	// scorer: checker chiqishning OXIRGI qatorida 0–100 oralig'ida son
	// qaytaradi. To'g'ri/noto'g'ri emas, sifat bahosi — NP-hard va
	// optimallashtirish masalalari uchun. Ball mutlaq: boshqalarning
	// yechimiga bog'liq emas, ya'ni qayta hisoblash zanjiri yo'q.
	Type string `json:"type"`
	// Interactive masalalarda ISHONCHLI interactor dasturi masala bilan
	// birga keladi. U sandbox TASHQARISIDA ishlaydi — u bizniki, submission
	// esa emas. Verdict interactor ning chiqish kodi bilan beriladi.
	Interactor *TrustedProgram `json:"interactor,omitempty"`
	// special va scorer uchun checker dasturi.
	Program *TrustedProgram `json:"program,omitempty"`
}

type Job struct {
	JobID     string `json:"job_id"`
	AttemptID int64  `json:"attempt_id"`
	//: Custom test bo'lsa to'ldiriladi; natijada qaytariladi.
	CustomRunID *int64    `json:"custom_run_id,omitempty"`
	Language    Language  `json:"language"`
	Source      string    `json:"source"`
	Limits      Limits    `json:"limits"`
	Tests       []Test    `json:"tests"`
	Checker     Checker   `json:"checker"`
	Subtasks    []Subtask `json:"subtasks,omitempty"`
	// acm | ioi | custom.
	// custom: chiqish kutilgan javob bilan SOLISHTIRILMAYDI — foydalanuvchi
	// o'z stdin'i bilan kodini sinab ko'ryapti (PRD P0-4).
	Mode string `json:"mode"`
	// Kirish validatori — test cheklovlarga mos ekanini tekshiruvchi
	// dastur (ADR-0020). Masala bilan keladi, ya'ni ishonchli; lekin
	// ishonchsiz kiritma ustida ishlaydi — `TrustedProgram` izohiga qarang.
	Validator *TrustedProgram `json:"validator,omitempty"`
	// Test kirishlari validatordan o'tkazilsinmi.
	//
	// ⚠️ Masalaning O'Z testlarini muallif yozgan, ya'ni ular ishonchli.
	// Ularni har yuborishda qayta tekshirish sof isrof bo'lardi
	// (test soni × har submission). Shuning uchun bayroq faqat job
	// ISHONCHSIZ kiritma olib kelganda yoqiladi — hack testi kabi.
	//
	// ⚠️ YOPIQ YIQILISH QOIDASI: bayroq `true` bo'lsa-yu, implementatsiya
	// validatorni qo'llab-quvvatlamasa, ish `IE` bilan RAD ETILISHI shart.
	// Jimgina o'tkazib yuborish validatsiyani butunlay o'chirib qo'yardi va
	// buzuq kiritma bilan istalgan to'g'ri yechimni «sindirish» mumkin
	// bo'lardi. Nomzodlar almashtiriladigan bo'lgani uchun bu xavf real.
	ValidateInput bool `json:"validate_input,omitempty"`
	// Hack dvigateli (ADR-0020) yuborgan ish — MARSHRUTLASH uchun.
	//
	// Judge hack mantig'ini bilmaydi va bilishi ham shart emas: u bu ikki
	// qiymatni shunchaki natijada qaytaradi, API esa javob qaysi hackning
	// qaysi bosqichiga tegishli ekanini shundan aniqlaydi. Bir hack uchta
	// ish ochadi (generator, etalon yechim, himoyachi) — bosqichsiz
	// javoblar aralashib ketardi.
	HackID    int64  `json:"hack_id,omitempty"`
	HackStage string `json:"hack_stage,omitempty"`
}

type TestResult struct {
	Index    int    `json:"index"`
	Verdict  string `json:"verdict"`
	TimeMS   int64  `json:"time_ms"`
	MemoryKB int64  `json:"memory_kb"`
	// Faqat custom rejimda to'ldiriladi: foydalanuvchiga chiqishni
	// qaytarish kerak. Oddiy tekshiruvda chiqish saqlanmaydi.
	Stdout string `json:"stdout,omitempty"`
}

type JudgeMeta struct {
	Worker         string `json:"worker"`
	Sandbox        string `json:"sandbox"`
	QueueWaitMS    int64  `json:"queue_wait_ms"`
	SandboxSetupMS int64  `json:"sandbox_setup_ms"`
	TotalMS        int64  `json:"total_ms"`
}

type Result struct {
	JobID string `json:"job_id"`
	// API natijani shu maydon orqali urinishga bog'laydi. Tushib qolsa
	// verdict hech qachon yozilmaydi va urinish PENDING qoladi.
	AttemptID   int64  `json:"attempt_id"`
	CustomRunID *int64 `json:"custom_run_id,omitempty"`
	// Ishdan AYNAN ko'chiriladi — hack natijasini bog'lash yo'li shu.
	HackID          int64        `json:"hack_id,omitempty"`
	HackStage       string       `json:"hack_stage,omitempty"`
	Verdict         string       `json:"verdict"`
	Score           int          `json:"score"`
	TimeMS          int64        `json:"time_ms"`
	MemoryKB        int64        `json:"memory_kb"`
	FailedTestIndex *int         `json:"failed_test_index"`
	CompileOutput   string       `json:"compile_output"`
	PerTest         []TestResult `json:"per_test"`
	Meta            JudgeMeta    `json:"judge_meta"`
}

// Verdict kodlari — 08-technical-spec dagi 20 talikning bake-off qismi.
const (
	VAC         = "AC"
	VWA         = "WA"
	VTLE        = "TLE"
	VMLE        = "MLE"
	VOLE        = "OLE"
	VRE         = "RE"
	VCE         = "CE"
	VCTimeout   = "COMPILE_TIMEOUT"
	VIdle       = "IDLENESS"
	VSecurity   = "SECURITY_VIOLATION"
	VIE         = "IE"
	VPartial    = "PARTIAL"
	VCheckerErr = "CHECKER_ERROR"
	VPE         = "PE"
	// RE ikkiga ajratilgan (DMOJ modeli): signal bilan o'ldirilgan dastur
	// va o'zi nolga teng bo'lmagan kod bilan chiqqan dastur — o'rganuvchi
	// uchun butunlay boshqa tuzatish. Eski `RE` bazadagi tarix uchun
	// qoladi, judge endi uni chiqarmaydi.
	VRESignal = "RE_SIGNAL"
	VREExit   = "RE_EXIT"
	// Masala TAYYOR EMAS: test yo'q, generator yiqilgan. Muallif aybi,
	// foydalanuvchiniki emas — `IE` bilan bir kodda bo'lsa, foydalanuvchi
	// platformani buzuq deb o'ylaydi.
	VWrongTest = "WRONG_TEST"
)
