import { describe, expect, it } from "vitest";

import {
  runningTargetFrom,
  tickRunningTestDisplay,
} from "@/features/submissions/runningTestStepper";

describe("tickRunningTestDisplay", () => {
  it("increments toward target one step per tick", () => {
    let display: Record<number, number> = {};
    display = tickRunningTestDisplay(display, { 1: 5 });
    expect(display[1]).toBe(1);
    display = tickRunningTestDisplay(display, { 1: 5 });
    expect(display[1]).toBe(2);
    for (let i = 0; i < 10; i++) {
      display = tickRunningTestDisplay(display, { 1: 5 });
    }
    expect(display[1]).toBe(5);
  });

  it("uses max of patch and server index as target", () => {
    expect(
      runningTargetFrom({ verdict: "RUNNING", running_test_index: 40 }, "RUNNING", 65),
    ).toBe(65);
  });
});
