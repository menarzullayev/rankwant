import { describe, expect, it } from "vitest";
import {
  DEFAULT_VERDICT_VARIANT,
  clampVerdictVariant,
  isPendingVerdict,
  verdictColors,
  verdictOf,
} from "@/lib/theme/verdict";

describe("verdictOf", () => {
  it("normalises case, spaces and dashes", () => {
    expect(verdictOf("rate-limited")?.key).toBe("RATE_LIMITED");
    expect(verdictOf(" denial of judgement ")?.key).toBe("DENIAL_OF_JUDGEMENT");
  });

  // An unknown code must stay visible as a raw code, never pass for "pending".
  it("returns null for an unknown code instead of guessing", () => {
    expect(verdictOf("SOMETHING_NEW")).toBeNull();
    expect(verdictOf(undefined)).toBeNull();
    expect(verdictColors(null)).toEqual(verdictColors(verdictOf("DENIAL_OF_JUDGEMENT")));
  });
});

describe("isPendingVerdict", () => {
  it("keeps polling while a rejudge is on its way", () => {
    expect(isPendingVerdict("pending")).toBe(true);
    expect(isPendingVerdict("RUNNING")).toBe(true);
    expect(isPendingVerdict("testing-aborted")).toBe(true);
  });

  it("stops for final or missing verdicts", () => {
    expect(isPendingVerdict("RATE_LIMITED")).toBe(false);
    expect(isPendingVerdict(null)).toBe(false);
  });
});

describe("clampVerdictVariant", () => {
  it("accepts a known variant and replaces anything else with the default", () => {
    expect(clampVerdictVariant("circle")).toBe("circle");
    expect(clampVerdictVariant("not-a-variant")).toBe(DEFAULT_VERDICT_VARIANT);
    expect(clampVerdictVariant(42)).toBe(DEFAULT_VERDICT_VARIANT);
  });
});
