import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  LANGUAGE_FILE_SAMPLES,
  LANGUAGE_SAMPLES,
  sampleFileForLanguage,
  sampleForLanguage,
} from "@/content/about/language-samples";

const CATALOG = new URL("../../../api/problems/languages.py", import.meta.url);

// The samples are code shown on `/about` for a visitor to copy. They sit in
// template literals, where a backslash and `${` mean something: until
// 2026-11-14 the generator wrote the code in unescaped, and the page showed
// `split(/s+/)` for JavaScript — a program that splits on the letter "s".
// `tools/check_language_samples.py` holds the file to its sources; these
// cases hold what the reader sees.
describe("language samples", () => {
  it("keeps a regular expression's backslash", () => {
    expect(LANGUAGE_SAMPLES.js24).toContain("split(/\\s+/)");
    expect(LANGUAGE_SAMPLES.ts24).toContain("split(/\\s+/)");
    expect(LANGUAGE_SAMPLES.php84).toContain("preg_split('/\\s+/', $in)");
    expect(LANGUAGE_SAMPLES.dart313).toContain("RegExp(r'\\s+')");
  });

  it("keeps an escape sequence inside a string of the sample", () => {
    expect(LANGUAGE_SAMPLES.prolog92).toContain('" \\t"');
    expect(LANGUAGE_FILE_SAMPLES.swift60).toContain('last == "\\n"');
  });

  it("keeps another language's own interpolation as text", () => {
    expect(LANGUAGE_FILE_SAMPLES.dart313).toContain(
      "'${int.parse(parts[0]) + int.parse(parts[1])}'",
    );
  });

  it("has a sample of both kinds for every language of the catalog", () => {
    const catalog = readFileSync(CATALOG, "utf8");
    const codes = [...catalog.matchAll(/"code": "([a-z][a-z0-9]*)"/g)].map((match) => match[1]);
    expect(codes.length).toBeGreaterThan(30);
    for (const code of codes) {
      expect(sampleForLanguage(code), code).toBeTruthy();
      expect(sampleFileForLanguage(code), code).toBeTruthy();
    }
  });
});
