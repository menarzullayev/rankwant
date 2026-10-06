import { describe, expect, it } from "vitest";

import { highlight } from "@/lib/highlight";

const kinds = (source: string, language: string) =>
  highlight(source, language)
    .filter((token) => token.kind !== "plain")
    .map((token) => `${token.kind}:${token.text}`);

describe("highlight", () => {
  it("always joins back to the source", () => {
    for (const [source, language] of [
      ["int main() { return 0; } // done", "cpp23"],
      ["a, b = map(int, input().split())  # read\nprint(a + b)", "py313"],
      ["fn f<'a>(x: &'a str) -> &'a str { x }", "rust185"],
      ['s = "unterminated\nprint(s)', "py313"],
      ["/* never closed", "c17"],
      ["", "cpp23"],
    ]) {
      expect(highlight(source, language).map((token) => token.text).join("")).toBe(source);
    }
  });

  it("marks comments, strings, numbers and keywords", () => {
    expect(kinds('return "a" + 12; // x', "cpp23")).toEqual([
      "keyword:return",
      'string:"a"',
      "number:12",
      "comment:// x",
    ]);
  });

  it("reads the comment marker from the language", () => {
    expect(kinds("x = 1 # note", "py313")).toEqual(["number:1", "comment:# note"]);
    // In C++ a hash is not a comment: `#include` stays code.
    expect(kinds("#include <cstdio>", "cpp23")).toEqual(["keyword:include"]);
    expect(kinds("x = 1 -- note", "haskell96")).toEqual(["number:1", "comment:-- note"]);
  });

  it("does not let a lone apostrophe swallow the rest of the file", () => {
    const tokens = highlight("fn f<'a>() {}\nreturn 1;", "rust185");
    expect(tokens.some((token) => token.kind === "keyword" && token.text === "return")).toBe(true);
  });
});
