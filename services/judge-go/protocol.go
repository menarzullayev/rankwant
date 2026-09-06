package main

// Shartnoma: services/bakeoff/protocol.md
// Bu tuzilmalar judge-py bilan BIR XIL bo'lishi shart — nomzodlar almashtiriladigan.

type Language struct {
	Code    string   `json:"code"`
	Compile []string `json:"compile"`
	Run     []string `json:"run"`
}

type Limits struct {
	CompileTimeMS int `json:"compile_time_ms"`
	TimeMS        int `json:"time_ms"`
	MemoryKB      int `json:"memory_kb"`
	OutputKB      int `json:"output_kb"`
	Processes     int `json:"processes"`
}

type Test struct {
	Index    int    `json:"index"`
	Input    string `json:"input"`
	Expected string `json:"expected"`
	// API test ma'lumotini emas, S3 havolasini yuboradi (08-technical-spec).
	// Inline maydonlar bake-off harness'i uchun qoladi.
	InputRef    string `json:"input_ref"`
	ExpectedRef string `json:"output_ref"`
}

type Interactor struct {
	Code    string   `json:"code"`
	Compile []string `json:"compile"`
	Run     []string `json:"run"`
	Source  string   `json:"source"`
}

type Checker struct {
	Type string `json:"type"` // standard | interactive
	// Interactive masalalarda ISHONCHLI interactor dasturi masala bilan
	// birga keladi. U sandbox TASHQARISIDA ishlaydi — u bizniki, submission
	// esa emas. Verdict interactor ning chiqish kodi bilan beriladi.
	Interactor *Interactor `json:"interactor,omitempty"`
}

type Job struct {
	JobID     string `json:"job_id"`
	AttemptID int64  `json:"attempt_id"`
	//: Custom test bo'lsa to'ldiriladi; natijada qaytariladi.
	CustomRunID *int64   `json:"custom_run_id,omitempty"`
	Language    Language `json:"language"`
	Source      string   `json:"source"`
	Limits      Limits   `json:"limits"`
	Tests       []Test   `json:"tests"`
	Checker     Checker  `json:"checker"`
	// acm | ioi | custom.
	// custom: chiqish kutilgan javob bilan SOLISHTIRILMAYDI — foydalanuvchi
	// o'z stdin'i bilan kodini sinab ko'ryapti (PRD P0-4).
	Mode string `json:"mode"`
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
	AttemptID       int64        `json:"attempt_id"`
	CustomRunID     *int64       `json:"custom_run_id,omitempty"`
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
	VAC       = "AC"
	VWA       = "WA"
	VTLE      = "TLE"
	VMLE      = "MLE"
	VOLE      = "OLE"
	VRE       = "RE"
	VCE       = "CE"
	VCTimeout = "COMPILE_TIMEOUT"
	VIdle     = "IDLENESS"
	VSecurity = "SECURITY_VIOLATION"
	VIE       = "IE"
)
