import { runInNewContext } from "node:vm";
import { describe, expect, it } from "vitest";

import type { ThemeTemplate } from "@/lib/api";
import { styleInit, teamDefaultLiteral } from "@/lib/theme/first-paint";
import { accountTemplates, mergeSavedTemplates } from "@/lib/theme/saved-templates";

const tpl = (name: string, style: string): ThemeTemplate => ({
  name,
  appearance: { style },
  a11y: {},
});

// APP-13: a new device never loaded the account's templates, and its first
// change sent an empty list that wiped them.
describe("mergeSavedTemplates", () => {
  it("lets the account's copy win a name clash, whatever the case", () => {
    const merged = mergeSavedTemplates([tpl("Tun", "terminal")], [tpl("tun", "clay")], 5);
    expect(merged).toEqual([tpl("Tun", "terminal")]);
  });

  it("keeps templates that exist only on the device, after the account's", () => {
    const merged = mergeSavedTemplates([tpl("Tun", "terminal")], [tpl("Ish", "swiss")], 5);
    expect(merged.map((row) => row.name)).toEqual(["Tun", "Ish"]);
  });

  it("cuts at the limit and keeps the account's first", () => {
    const account = ["A", "B", "C", "D"].map((name) => tpl(name, "clay"));
    const device = ["E", "F"].map((name) => tpl(name, "clay"));
    expect(mergeSavedTemplates(account, device, 5).map((row) => row.name)).toEqual([
      "A",
      "B",
      "C",
      "D",
      "E",
    ]);
  });

  it("returns either list alone when the other is empty", () => {
    expect(mergeSavedTemplates([], [tpl("Ish", "swiss")], 5)).toEqual([tpl("Ish", "swiss")]);
    expect(mergeSavedTemplates([tpl("Tun", "terminal")], [], 5)).toEqual([tpl("Tun", "terminal")]);
  });

  it("reads an account without a templates group as none", () => {
    expect(accountTemplates(undefined)).toEqual([]);
    expect(accountTemplates({})).toEqual([]);
    expect(accountTemplates({ templates: [tpl("Tun", "terminal")] })).toHaveLength(1);
  });
});

/** Runs a first-paint script against a fake `localStorage` and `<html>`. */
function paint(script: string, stored: Record<string, string>, broken = false): Record<string, string> {
  const dataset: Record<string, string> = {};
  runInNewContext(script, {
    localStorage: {
      getItem: (key: string) => {
        if (broken) throw new Error("storage blocked");
        return stored[key] ?? null;
      },
    },
    document: { documentElement: { dataset } },
  });
  return dataset;
}

// APP-14: the first paint used a fixed `clay`, whatever the team default was.
describe("first paint", () => {
  it("uses the team default style when the device has none", () => {
    expect(paint(styleInit("glass"), {}).style).toBe("glass");
  });

  it("keeps the visitor's own style over the team default", () => {
    expect(paint(styleInit("glass"), { style: "terminal" }).style).toBe("terminal");
  });

  it("falls back to the team default when storage is blocked", () => {
    expect(paint(styleInit("glass"), {}, true).style).toBe("glass");
  });

  it("embeds the team default so that it cannot close the script tag", () => {
    const literal = teamDefaultLiteral({ style: "</script><script>alert(1)//" });
    expect(literal).not.toContain("</");
    expect(JSON.parse(runInNewContext(literal) as string)).toEqual({
      style: "</script><script>alert(1)//",
    });
  });
});
