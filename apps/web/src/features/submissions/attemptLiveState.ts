/** Jonli urinish holati — SSE hodisalaridan yig'iladi (REST haqiqat manbasi). */

export type LiveTestRow = {
  verdict: string;
  time_ms?: number;
  memory_kb?: number;
  status: "done" | "running";
};

export type AttemptLiveState = {
  phase?: "compiling" | "running";
  totalTests?: number;
  runningIndex?: number | null;
  verdict?: string;
  tests: Record<number, LiveTestRow>;
};

export function emptyLiveState(): AttemptLiveState {
  return { tests: {} };
}

export function reduceLiveState(
  prev: AttemptLiveState,
  event: string,
  data: Record<string, unknown> | null,
): AttemptLiveState {
  if (!data) return prev;
  const next: AttemptLiveState = {
    ...prev,
    tests: { ...prev.tests },
  };

  if (event === "attempt_queued") {
    if (typeof data.verdict === "string") next.verdict = data.verdict;
    return next;
  }

  if (event === "compilation_started") {
    next.phase = "compiling";
    const total = data.total_tests;
    if (typeof total === "number") next.totalTests = total;
    if (typeof data.verdict === "string") next.verdict = data.verdict;
    return next;
  }

  if (event === "compilation_finished") {
    next.phase = data.ok ? "running" : prev.phase;
    if (typeof data.verdict === "string") next.verdict = data.verdict;
    return next;
  }

  if (event === "attempt_progress" || event === "test_started") {
    next.phase = "running";
    const idx = data.running_test_index;
    if (typeof idx === "number") {
      next.runningIndex = idx;
      const existing = next.tests[idx];
      if (!existing || existing.status !== "done") {
        next.tests[idx] = { verdict: "RUNNING", status: "running" };
      }
    }
    if (typeof data.total_tests === "number") next.totalTests = data.total_tests;
    if (typeof data.verdict === "string") next.verdict = data.verdict;
    return next;
  }

  if (event === "test_finished") {
    next.phase = "running";
    const idx = data.test_index;
    if (typeof idx === "number") {
      next.tests[idx] = {
        verdict: String(data.verdict ?? "IE"),
        time_ms: typeof data.time_ms === "number" ? data.time_ms : undefined,
        memory_kb: typeof data.memory_kb === "number" ? data.memory_kb : undefined,
        status: "done",
      };
    }
    if (typeof data.running_test_index === "number") {
      next.runningIndex = data.running_test_index;
    }
    return next;
  }

  if (event === "verdict" || event === "attempt_finished") {
    if (typeof data.verdict === "string") next.verdict = data.verdict;
    next.runningIndex = null;
    return next;
  }

  return prev;
}

export function completedTestCount(state: AttemptLiveState): number {
  return Object.values(state.tests).filter((t) => t.status === "done").length;
}
