import { describe, expect, it } from "vitest";

import { mergeAttemptRow } from "@/features/submissions/attemptLiveOverlay";
import type { Attempt } from "@/lib/api";

const base: Attempt = {
  id: 1,
  username: "demo",
  user_title: null,
  problem: "a-plus-b",
  problem_title: "A + B",
  problem_code: 1,
  contest: null,
  language: "cpp23",
  language_name: "C++23",
  verdict: "PENDING",
  score: 0,
  time_ms: 0,
  memory_kb: 0,
  failed_test_index: null,
  running_test_index: null,
  created_at: "2026-01-01T00:00:00Z",
  judged_at: null,
  source_size: 100,
  is_first_solver: false,
};

describe("mergeAttemptRow", () => {
  it("applies SSE patch while server row is still pending", () => {
    const merged = mergeAttemptRow(base, {
      verdict: "RUNNING",
      running_test_index: 3,
    });
    expect(merged.verdict).toBe("RUNNING");
    expect(merged.running_test_index).toBe(3);
  });

  it("applies SSE patch when refresh still shows AC", () => {
    const merged = mergeAttemptRow(
      { ...base, verdict: "AC", running_test_index: null },
      { verdict: "RUNNING", running_test_index: 4 },
    );
    expect(merged.verdict).toBe("RUNNING");
    expect(merged.running_test_index).toBe(4);
  });

  it("ignores patch when both sides are final", () => {
    const merged = mergeAttemptRow(
      { ...base, verdict: "WA", running_test_index: 1 },
      { verdict: "AC", running_test_index: null },
    );
    expect(merged.verdict).toBe("WA");
  });
});
