import { describe, expect, it } from "vitest";

import { ABOUT_VERDICT_ORDER } from "@/content/about/verdict-guide-order";
import { ABOUT_SECTIONS, VERDICT_GROUPS } from "@/features/about/sections";
import { PREFERRED_LANGUAGES, defaultLanguage } from "@/lib/editor-language";

describe("about page sections", () => {
  it("keeps the anchors people have already shared", () => {
    expect(ABOUT_SECTIONS.map((section) => section.id)).toEqual([
      "journey",
      "submit",
      "languages",
      "verdicts",
      "practices",
      "judge",
    ]);
  });

  it("puts every verdict code in exactly one group", () => {
    const grouped = VERDICT_GROUPS.flatMap((group) => group.codes);
    expect([...grouped].sort()).toEqual([...ABOUT_VERDICT_ORDER].sort());
    expect(new Set(grouped).size).toBe(grouped.length);
  });

  it("leads with what a solver meets every day", () => {
    expect(VERDICT_GROUPS[0].id).toBe("common");
    expect(VERDICT_GROUPS[0].codes).toEqual(expect.arrayContaining(["AC", "WA", "TLE", "CE"]));
    expect(VERDICT_GROUPS[2].codes).toContain("DENIAL_OF_JUDGEMENT");
  });
});

describe("the sample's first language", () => {
  const all = [{ code: "ada14" }, { code: "java21" }, { code: "py313" }, { code: "cpp23" }];

  it("is the one the editor opens on, not the first by name", () => {
    expect(defaultLanguage(all)).toBe("cpp23");
    expect(PREFERRED_LANGUAGES[0]).toBe("cpp23");
  });

  it("falls back down the list, then to whatever there is", () => {
    expect(defaultLanguage([{ code: "ada14" }, { code: "py313" }])).toBe("py313");
    expect(defaultLanguage([{ code: "ada14" }])).toBe("ada14");
    expect(defaultLanguage([])).toBe("");
  });
});
