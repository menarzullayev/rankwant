import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  DEFAULT_THEME_TOGGLE,
  THEME_TOGGLES,
  clampThemeToggle,
  themeToggleToEffect,
} from "@/lib/theme/toggle";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

describe("H6 theme toggle", () => {
  it("defaults to doira and maps page effects", () => {
    expect(DEFAULT_THEME_TOGGLE).toBe("doira");
    expect(clampThemeToggle(undefined)).toBe("doira");
    expect(clampThemeToggle("chip")).toBe("doira");
    expect(themeToggleToEffect("doira")).toBe("circle");
    expect(themeToggleToEffect("parda")).toBe("curtain");
    expect(themeToggleToEffect("aylanma")).toBe("fade");
    expect(THEME_TOGGLES).toEqual([
      "aylanma",
      "relss",
      "doira",
      "ufq",
      "morph",
      "osmon",
      "parda",
    ]);
  });

  it("wires customizer picker and header mount", () => {
    const tab = src("../../src/components/customizer/AppearanceTab.tsx");
    const actions = src("../../src/layout/HeaderActions.tsx");
    const prefs = src("../../src/lib/prefs.ts");
    expect(tab).toContain("ThemeToggleSection");
    expect(tab).toContain("THEME_TOGGLES");
    expect(actions).toContain("<ThemeToggle");
    expect(prefs).toContain("themeToggleToEffect");
    expect(prefs).toContain('return "circle"');
  });
});
