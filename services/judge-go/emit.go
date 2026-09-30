package main

// Emit — oraliq judge hodisalarini natijalar navbatiga yuboradi (kind=…).
type Emit func(map[string]any)

func pushEmit(emit Emit, attemptID int64, kind string, fields map[string]any) {
	if emit == nil || attemptID <= 0 {
		return
	}
	msg := map[string]any{
		"kind":       kind,
		"attempt_id": attemptID,
	}
	for k, v := range fields {
		msg[k] = v
	}
	emit(msg)
}

func emitProgress(emit Emit, attemptID int64, testIndex int) {
	pushEmit(emit, attemptID, "progress", map[string]any{
		"running_test_index": testIndex,
		"verdict":            "RUNNING",
	})
}

func emitTestFinished(emit Emit, attemptID int64, tr TestResult) {
	pushEmit(emit, attemptID, "test_finished", map[string]any{
		"test_index": tr.Index,
		"verdict":    tr.Verdict,
		"time_ms":    tr.TimeMS,
		"memory_kb":  tr.MemoryKB,
	})
}
