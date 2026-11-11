import { describe, expect, it } from "vitest";

import { formatTolerance } from "../../src/lib/tolerance";

describe("the tolerance of a real-number problem", () => {
  it("writes a power of ten with a superscript", () => {
    expect(formatTolerance(1e-6)).toBe("10⁻⁶");
    expect(formatTolerance(1e-12)).toBe("10⁻¹²");
    expect(formatTolerance(0.1)).toBe("10⁻¹");
  });

  it("writes anything else in exponent form", () => {
    expect(formatTolerance(1.5e-5)).toBe("1.5e-5");
  });
});
