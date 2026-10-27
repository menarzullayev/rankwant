package main

import (
	"context"
	"strings"
	"testing"
)

// A job written for a newer shape is refused, not judged with fields this
// build does not know. Absent (0) is a pre-field job and is accepted.
func TestNewerProtocolIsRefused(t *testing.T) {
	job := &Job{JobID: "j", ProtocolVersion: ProtocolVersion + 1}
	res := judge(context.Background(), job, nil, nil)
	if res.Verdict != VIE {
		t.Fatalf("verdict = %s, want IE", res.Verdict)
	}
	if !strings.Contains(res.CompileOutput, "protocol_version") {
		t.Fatalf("reason missing: %q", res.CompileOutput)
	}
	if res.ProtocolVersion != ProtocolVersion {
		t.Fatalf("result must carry the judge's own version, got %d", res.ProtocolVersion)
	}
}

func TestOlderOrAbsentProtocolIsNotRefusedForVersion(t *testing.T) {
	for _, v := range []int{0, ProtocolVersion} {
		job := &Job{JobID: "j", ProtocolVersion: v}
		res := judge(context.Background(), job, nil, nil)
		if strings.Contains(res.CompileOutput, "protocol_version") {
			t.Fatalf("version %d refused: %q", v, res.CompileOutput)
		}
	}
}
