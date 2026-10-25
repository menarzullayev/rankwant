import { describe, expect, it } from "vitest";

import { uz } from "@/i18n/locales/uz";
import { CODE, VERDICTS, heatCells } from "@/features/auth/auth-panel-data";

describe("the /login brand panel's illustration data", () => {
  it("names only messages that exist", () => {
    for (const [, , key] of VERDICTS) {
      expect(uz).toHaveProperty(`auth.panel.${key}`);
    }
  });

  it("puts the `{n}` placeholder where a verdict message needs a test number", () => {
    for (const [, , key, n] of VERDICTS) {
      const message = uz[`auth.panel.${key}` as keyof typeof uz] as string;
      expect(message.includes("{n}")).toBe(n !== "");
    }
  });

  it("lays out 15 weeks of 7 days, row by row, the last week lit", () => {
    const cells = heatCells();
    expect(cells).toHaveLength(105);
    const lastWeek = cells.filter((_, index) => index % 15 === 14);
    expect(lastWeek).toEqual(Array(7).fill("cs"));
    expect(cells.filter((cell) => cell === "cs")).toHaveLength(7);
  });

  it("is a deterministic pattern", () => {
    expect(heatCells()).toEqual(heatCells());
  });

  it("keeps the code sample non-empty on every line", () => {
    for (const line of CODE) expect(line.length).toBeGreaterThan(0);
  });
});
