/** The algorithms library's sections and levels (ADR-0062).
 *
 *  The order follows the library: from number theory to the miscellany. The
 *  label keys are written out, not built from the slug, so every one is a
 *  key the dictionary checker can see. */

import type { BadgeColor } from "@/components/ui/Badge";
import type { MessageKey } from "@/i18n/messages";

export const CATEGORIES = [
  "algebra",
  "data-structures",
  "dynamic-programming",
  "string",
  "linear-algebra",
  "combinatorics",
  "num-methods",
  "geometry",
  "graph",
  "sequences",
  "game-theory",
  "schedules",
  "others",
] as const;

export type Category = (typeof CATEGORIES)[number];

export const CATEGORY_LABEL: Record<Category, MessageKey> = {
  algebra: "algorithms.category.algebra",
  "data-structures": "algorithms.category.dataStructures",
  "dynamic-programming": "algorithms.category.dynamicProgramming",
  string: "algorithms.category.string",
  "linear-algebra": "algorithms.category.linearAlgebra",
  combinatorics: "algorithms.category.combinatorics",
  "num-methods": "algorithms.category.numMethods",
  geometry: "algorithms.category.geometry",
  graph: "algorithms.category.graph",
  sequences: "algorithms.category.sequences",
  "game-theory": "algorithms.category.gameTheory",
  schedules: "algorithms.category.schedules",
  others: "algorithms.category.others",
};

export const LEVELS = ["beginner", "intermediate", "advanced"] as const;

export type Level = (typeof LEVELS)[number];

export const LEVEL_LABEL: Record<Level, MessageKey> = {
  beginner: "algorithms.level.beginner",
  intermediate: "algorithms.level.intermediate",
  advanced: "algorithms.level.advanced",
};

export const LEVEL_COLOR: Record<Level, BadgeColor> = {
  beginner: "success",
  intermediate: "info",
  advanced: "warning",
};

export const VIA_LABEL: Record<"pick" | "source" | "topic", MessageKey> = {
  pick: "algorithms.via.pick",
  source: "algorithms.via.source",
  topic: "algorithms.via.topic",
};

/** The licence the library's text is under (CC BY-SA 4.0). */
export const LICENCE_URL = "https://creativecommons.org/licenses/by-sa/4.0/";
/** Its name, written the same in every language. */
export const LICENCE_NAME = "CC BY-SA 4.0";

export function isCategory(value: string): value is Category {
  return (CATEGORIES as readonly string[]).includes(value);
}

export function isLevel(value: string | undefined): value is Level {
  return value !== undefined && (LEVELS as readonly string[]).includes(value);
}

export function algorithmPath(category: string, slug: string): string {
  return `/algorithms/${category}/${slug}`;
}
