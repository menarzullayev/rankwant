import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { isForeignWord, toNewAlphabet, toOldAlphabet } from "@rankwant/shared/alphabet";

// One set of cases for both converters (ADR-0059): the Python twin
// (`apps/api/core/alphabet.py`) runs the same file.
type Case = { old?: string; new: string; back?: string };
const file = JSON.parse(
  readFileSync(
    fileURLToPath(new URL("../../../../packages/shared/src/alphabet-cases.json", import.meta.url)),
    "utf8",
  ),
);
const cases: Case[] = file.cases;
const folds: { text: string; folded: string }[] = file.fold;

describe("toNewAlphabet", () => {
  for (const c of cases.filter((item) => item.old !== undefined)) {
    it(c.old!.slice(0, 40), () => expect(toNewAlphabet(c.old!)).toBe(c.new));
  }
  it("leaves new text as it is", () => {
    expect(toNewAlphabet(toNewAlphabet("Shart o'qing"))).toBe("Şart öqing");
  });
});

describe("toOldAlphabet", () => {
  for (const c of cases.filter((item) => item.back !== undefined)) {
    it(c.new.slice(0, 40), () => expect(toOldAlphabet(c.new)).toBe(c.back));
  }
});

describe("isForeignWord", () => {
  it.each(["GitHub", "SSH", "Shift", "Cache", "Python", "Türkçe"])("%s is kept", (word) => {
    expect(isForeignWord(word)).toBe(true);
  });
  it.each(["Shart", "o'qish", "chiqish", "yig'indi", "SHARTLAR"])("%s is Uzbek", (word) => {
    expect(isForeignWord(word)).toBe(false);
  });
});

describe("search fold", () => {
  it("treats both alphabets as one query", async () => {
    const { foldText, highlight } = await import("@/lib/search/model");
    expect(foldText("Özbekiston")).toBe(foldText("O'zbekiston"));
    expect(foldText("Çiqiş maʼlumoti")).toBe("chiqish malumoti");
    const parts = highlight("Şart va çiqiş", "shart");
    expect(parts[0]).toEqual({ text: "Şart", hit: true });
  });
});

describe("search fold, shared cases", () => {
  it.each(folds)("$text", async ({ text, folded }) => {
    const { foldText } = await import("@/lib/search/model");
    expect(foldText(text)).toBe(folded);
  });
});
