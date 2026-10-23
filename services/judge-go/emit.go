package main

import (
	"sync"
	"time"
)

// progressEvery — at most one progress/test_finished event per attempt in this
// window. A 100-test attempt used to push ~200 events; the API spent its time
// applying them, not the judge judging (measured 2026-10-23: judges done in
// 70 s, results backlog 21 000 events). The terminal result carries every
// test, so dropped progress events lose nothing but live granularity.
const progressEvery = 250 * time.Millisecond

var (
	progressMu   sync.Mutex
	progressLast = map[int64]time.Time{}
)

// progressDue reports whether a progress-type event for the attempt may be
// sent now, and records the send time.
func progressDue(attemptID int64, now time.Time) bool {
	progressMu.Lock()
	defer progressMu.Unlock()
	if len(progressLast) > 4096 {
		progressLast = map[int64]time.Time{}
	}
	if last, ok := progressLast[attemptID]; ok && now.Sub(last) < progressEvery {
		return false
	}
	progressLast[attemptID] = now
	return true
}

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
	if !progressDue(attemptID, time.Now()) {
		return
	}
	pushEmit(emit, attemptID, "progress", map[string]any{
		"running_test_index": testIndex,
		"verdict":            "RUNNING",
	})
}

func emitTestFinished(emit Emit, attemptID int64, tr TestResult) {
	if !progressDue(attemptID, time.Now()) {
		return
	}
	pushEmit(emit, attemptID, "test_finished", map[string]any{
		"test_index": tr.Index,
		"verdict":    tr.Verdict,
		"time_ms":    tr.TimeMS,
		"memory_kb":  tr.MemoryKB,
	})
}
