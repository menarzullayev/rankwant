import { describe, expect, it } from "vitest";

import {
  HERO_DIFFICULTY_MAX,
  HERO_SAMPLE_MAX,
  heroSample,
  pickHeroProblem,
  plainStatement,
} from "@/app/(site)/_home/hero-model";
import type { Problem, Sample } from "@/lib/api";

const problem = (slug: string, tests: boolean, difficulty: number) =>
  ({ slug, has_tests: tests, difficulty }) as Problem;

describe("pickHeroProblem", () => {
  it("takes the first (most opened) problem that has tests and is easy to read", () => {
    const list = [
      problem("hard", true, 2000),
      problem("no-tests", false, 800),
      problem("a-plus-b", true, 800),
      problem("later", true, 900),
    ];
    expect(pickHeroProblem(list)?.slug).toBe("a-plus-b");
  });

  it("accepts the difficulty limit itself and nothing above it", () => {
    expect(pickHeroProblem([problem("edge", true, HERO_DIFFICULTY_MAX)])?.slug).toBe("edge");
    expect(pickHeroProblem([problem("over", true, HERO_DIFFICULTY_MAX + 1)])).toBeNull();
  });

  it("is null when nothing fits, so the hero draws without a card", () => {
    expect(pickHeroProblem([])).toBeNull();
  });
});

describe("plainStatement", () => {
  it("returns the first paragraph and drops the rest", () => {
    expect(plainStatement("Two numbers are given.\n\nSecond paragraph.")).toBe(
      "Two numbers are given.",
    );
  });

  it("keeps the words of formulas, code, emphasis, links and headings", () => {
    const text = plainStatement("# Title\n\nGiven $a$ and `b`, **print** the [sum](https://x.y).");
    expect(text).toBe("Given a and b, print the sum.");
  });

  it("cuts a long paragraph at a word boundary and marks the cut", () => {
    const long = "word ".repeat(100);
    const out = plainStatement(long, 40);
    expect(out.endsWith("…")).toBe(true);
    expect(out.length).toBeLessThanOrEqual(41);
    expect(out.slice(0, -1).endsWith("word")).toBe(true);
  });

  it("is empty for an empty statement", () => {
    expect(plainStatement("")).toBe("");
    expect(plainStatement("   \n\n  ")).toBe("");
  });
});

describe("heroSample", () => {
  const sample = (input: string, expected: string): Sample => ({ order: 1, input, expected });

  it("takes the first sample short enough to print", () => {
    const long = "x".repeat(HERO_SAMPLE_MAX + 1);
    expect(heroSample([sample(long, "1"), sample("2 3", "5")])?.expected).toBe("5");
  });

  it("is null when every sample is too long", () => {
    const long = "x".repeat(HERO_SAMPLE_MAX + 1);
    expect(heroSample([sample(long, "1")])).toBeNull();
    expect(heroSample([])).toBeNull();
  });
});
