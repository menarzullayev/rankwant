import type { Problem, Sample } from "@/lib/api";

/**
 * Pure helpers of the guest hero (decision 2026-11-15): which public problem the card
 * shows, and how its statement becomes one short plain-text paragraph.
 */

/** The card shows a beginner problem: an easy one reads in a glance. */
export const HERO_DIFFICULTY_MAX = 1200;

/** Longest sample input the card prints; a longer one would break the card's height. */
export const HERO_SAMPLE_MAX = 80;

/** The most opened problem the judge can test and a newcomer can read — the list arrives
 *  ordered by openings, so the first match is the pick. */
export function pickHeroProblem(problems: Problem[]): Problem | null {
  return problems.find((p) => p.has_tests && p.difficulty <= HERO_DIFFICULTY_MAX) ?? null;
}

/** The first Markdown paragraph of prose as plain text, cut at a word boundary. Formulas
 *  (`$a+b$`), code ticks, emphasis, links and headings lose their markup but keep
 *  their words. */
export function plainStatement(markdown: string, max = 220): string {
  const first =
    markdown
      .split(/\n\s*\n/)
      .map((part) => part.trim())
      // A heading is not the statement: skip to the first paragraph of prose.
      .find((part) => part !== "" && !/^#{1,6}\s/.test(part)) ?? "";
  const text = first
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/\$\$?([^$]+)\$\$?/g, "$1")
    .replace(/[`*_]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  const space = cut.lastIndexOf(" ");
  return `${(space > max / 2 ? cut.slice(0, space) : cut).trimEnd()}…`;
}

/** The first sample short enough to print. */
export function heroSample(samples: Sample[]): Sample | null {
  return (
    samples.find(
      (s) => s.input.length <= HERO_SAMPLE_MAX && s.expected.length <= HERO_SAMPLE_MAX,
    ) ?? null
  );
}
