import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  LANGUAGE_FAMILIES,
  editorLanguage,
  languageFamily,
  starterSource,
} from "@/lib/editor-language";

const CATALOG = new URL("../../../api/problems/languages.py", import.meta.url);

describe("editorLanguage", () => {
  it("gives each judge language its Monaco grammar", () => {
    const codes = ["c17", "cpp23", "csharp14", "go124", "java21"];
    expect(codes.map(editorLanguage)).toEqual(["c", "cpp", "csharp", "go", "java"]);
    const more = ["js24", "kotlin24", "php84", "py313", "rust185"];
    expect(more.map(editorLanguage)).toEqual([
      "javascript",
      "kotlin",
      "php",
      "python",
      "rust",
    ]);
  });

  // The prefix match this replaced gave `kotlin24` and `php84` plain text and
  // would have given `c17` nothing at all.
  it("looks up the family, not a prefix", () => {
    expect(languageFamily("csharp14")).toBe("csharp");
    expect(languageFamily("CPP23")).toBe("cpp");
    expect(editorLanguage("cs")).toBe("plaintext");
  });

  it("edits an unknown language as plain text", () => {
    expect(editorLanguage("zz1")).toBe("plaintext");
    // A plain object would resolve inherited names such as this one.
    expect(editorLanguage("constructor")).toBe("plaintext");
  });

  // A catalog code missing here is judged fine but edited as plain text with
  // no starter code, and nothing else notices.
  it("covers every language in the judge catalog", () => {
    const catalog = readFileSync(CATALOG, "utf8");
    const codes = [...catalog.matchAll(/"code": "([a-z][a-z0-9]*)"/g)].map(
      (match) => match[1] ?? "",
    );
    expect(codes.length).toBeGreaterThanOrEqual(10);
    const missing = codes.filter(
      (code) => !LANGUAGE_FAMILIES.has(languageFamily(code)),
    );
    expect(missing).toEqual([]);
  });
});

describe("starterSource", () => {
  it("names the class the judge runs for Java", () => {
    expect(starterSource("java21")).toContain("public class Main");
  });

  it("opens PHP in code mode", () => {
    expect(starterSource("php84").startsWith("<?php")).toBe(true);
  });

  it("imports nothing in Go, where an unused import does not compile", () => {
    expect(starterSource("go124")).not.toContain("import");
  });

  it("leaves scripts and unknown languages empty", () => {
    expect(starterSource("py313")).toBe("");
    expect(starterSource("js24")).toBe("");
    expect(starterSource("zz1")).toBe("");
  });
});
