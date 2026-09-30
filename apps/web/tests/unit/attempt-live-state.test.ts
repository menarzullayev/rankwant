import { describe, expect, it } from "vitest";

import {
  completedTestCount,
  emptyLiveState,
  reduceLiveState,
} from "@/features/submissions/attemptLiveState";

describe("reduceLiveState", () => {
  it("tracks compilation and per-test results", () => {
    let state = emptyLiveState();
    state = reduceLiveState(state, "compilation_started", {
      total_tests: 3,
      verdict: "RUNNING",
    });
    expect(state.phase).toBe("compiling");
    expect(state.totalTests).toBe(3);

    state = reduceLiveState(state, "attempt_progress", {
      running_test_index: 1,
      verdict: "RUNNING",
    });
    expect(state.tests[1]?.status).toBe("running");

    state = reduceLiveState(state, "test_finished", {
      test_index: 1,
      verdict: "AC",
      time_ms: 5,
      memory_kb: 100,
    });
    expect(state.tests[1]?.verdict).toBe("AC");
    expect(state.tests[1]?.status).toBe("done");
    expect(completedTestCount(state)).toBe(1);
  });

  it("handles attempt_queued and test_started like progress", () => {
    let state = emptyLiveState();
    state = reduceLiveState(state, "attempt_queued", { verdict: "PENDING" });
    expect(state.verdict).toBe("PENDING");

    state = reduceLiveState(state, "test_started", {
      running_test_index: 2,
      total_tests: 5,
      verdict: "RUNNING",
    });
    expect(state.runningIndex).toBe(2);
    expect(state.totalTests).toBe(5);
    expect(state.tests[2]?.status).toBe("running");
  });
});
