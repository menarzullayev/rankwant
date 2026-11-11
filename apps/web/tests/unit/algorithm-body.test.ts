import { describe, expect, it } from "vitest";

import { withoutPracticeSection, withoutTitle } from "@/features/algorithms/body";

describe("algorithm article body", () => {
  it("drops its own title line", () => {
    expect(withoutTitle("# Dijkstra {#dijkstra}\n\nText")).toBe("Text");
    expect(withoutTitle("Text\n# Not first")).toBe("Text\n# Not first");
  });

  it("drops the practice section up to the next heading of its level", () => {
    const body = [
      "## Algorithm {#algorithm}",
      "text",
      "## Practice Problems {#practice-problems}",
      "- [CF 1](https://codeforces.com/contest/1/problem/A)",
      "### sub",
      "- more",
      "## Afterword {#afterword}",
      "end",
    ].join("\n");
    expect(withoutPracticeSection(body)).toBe(
      ["## Algorithm {#algorithm}", "text", "## Afterword {#afterword}", "end"].join("\n"),
    );
  });

  it("drops a last practice section to the end", () => {
    expect(withoutPracticeSection("## A {#a}\nx\n## Mashq {#practice-problems}\n- [x](y)\n")).toBe(
      "## A {#a}\nx\n",
    );
  });

  it("ignores a heading inside code and keeps a text without the section", () => {
    const body = "```md\n## Practice {#practice-problems}\n```\nrest";
    expect(withoutPracticeSection(body)).toBe(body);
  });
});
