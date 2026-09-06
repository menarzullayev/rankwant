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
}

type Checker struct {
	Type string `json:"type"` // standard | interactive
}

type Job struct {
	JobID     string   `json:"job_id"`
	AttemptID int64    `json:"attempt_id"`
	Language  Language `json:"language"`
	Source    string   `json:"source"`
	Limits    Limits   `json:"limits"`
	Tests     []Test   `json:"tests"`
	Checker   Checker  `json:"checker"`
	Mode      string   `json:"mode"` // acm | ioi
}

type TestResult struct {
	Index    int    `json:"index"`
	Verdict  string `json:"verdict"`
	TimeMS   int64  `json:"time_ms"`
	MemoryKB int64  `json:"memory_kb"`
}

type JudgeMeta struct {
	Worker         string `json:"worker"`
	Sandbox        string `json:"sandbox"`
	QueueWaitMS    int64  `json:"queue_wait_ms"`
	SandboxSetupMS int64  `json:"sandbox_setup_ms"`
	TotalMS        int64  `json:"total_ms"`
}

type Result struct {
	JobID           string       `json:"job_id"`
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
