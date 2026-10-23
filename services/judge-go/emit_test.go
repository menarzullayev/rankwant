package main

import (
	"testing"
	"time"
)

func TestProgressDueThrottlesPerAttempt(t *testing.T) {
	start := time.Unix(1000, 0)
	if !progressDue(9001, start) {
		t.Fatal("first event must pass")
	}
	if progressDue(9001, start.Add(10*time.Millisecond)) {
		t.Fatal("event inside the window must be dropped")
	}
	if !progressDue(9002, start.Add(10*time.Millisecond)) {
		t.Fatal("another attempt is independent")
	}
	if !progressDue(9001, start.Add(progressEvery)) {
		t.Fatal("event after the window must pass")
	}
}
