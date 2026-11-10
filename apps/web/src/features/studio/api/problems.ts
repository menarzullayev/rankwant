/** `/studio/problems` — the author's own drafts (ADR-0025, 2026-11-10).
 *
 *  Two API surfaces: `problems/mine/` for the draft itself and the review
 *  request, `staff/problems/<slug>/tests/` for its tests (that action lets
 *  a draft's author in, the rest of the staff surface does not).
 */

import {
  deleteJson,
  getJson,
  patchJson,
  postJson,
  type Paginated,
} from "@/lib/api/client";

/** `problems.author_views.MAX_DRAFTS` — the rule `studio_problems_panel`
 *  keeps the two equal. */
export const STUDIO_DRAFT_LIMIT = 20;

export const DIFFICULTY_MIN = 800;
export const DIFFICULTY_MAX = 3500;
export const DIFFICULTY_STEP = 100;

export type MineProblem = {
  slug: string;
  title: string;
  statement: string;
  input_format: string;
  output_format: string;
  note: string;
  editorial: string;
  difficulty: number;
  time_limit_ms: number;
  memory_limit_kb: number;
  is_public: boolean;
  review_requested_at: string | null;
  sample_count: number;
  hidden_count: number;
  created_at: string;
  updated_at: string;
};

export type MineProblemInput = Partial<
  Pick<
    MineProblem,
    | "slug"
    | "title"
    | "statement"
    | "input_format"
    | "output_format"
    | "note"
    | "editorial"
    | "difficulty"
  >
>;

export type DraftTest = {
  id: number;
  order: number;
  is_sample: boolean;
  group: string;
  points: number;
};

export type DraftTestInput = {
  order: number;
  input: string;
  expected: string;
  is_sample: boolean;
};

/** What `review` reports missing — `problems.author_views.review_gaps`. */
export type ReviewGap = "statement" | "sample_test" | "hidden_test";

export type DraftStatus = "public" | "review" | "draft";

export function draftStatus(problem: Pick<MineProblem, "is_public" | "review_requested_at">): DraftStatus {
  if (problem.is_public) return "public";
  if (problem.review_requested_at) return "review";
  return "draft";
}

/** The same three checks the server makes before it accepts a review. */
export function reviewGaps(
  problem: Pick<MineProblem, "statement" | "sample_count" | "hidden_count">,
): ReviewGap[] {
  const gaps: ReviewGap[] = [];
  if (!problem.statement.trim()) gaps.push("statement");
  if (problem.sample_count < 1) gaps.push("sample_test");
  if (problem.hidden_count < 1) gaps.push("hidden_test");
  return gaps;
}

const MINE = "/problems/mine/";
const one = (slug: string) => `${MINE}${encodeURIComponent(slug)}/`;
const tests = (slug: string) => `/staff/problems/${encodeURIComponent(slug)}/tests/`;

export const studioProblems = {
  list: () => getJson<Paginated<MineProblem>>(MINE),
  get: (slug: string) => getJson<MineProblem>(one(slug)),
  create: (body: MineProblemInput) => postJson<MineProblem>(MINE, body),
  update: (slug: string, body: MineProblemInput) => patchJson<MineProblem>(one(slug), body),
  remove: (slug: string) => deleteJson<void>(one(slug)),
  review: (slug: string) => postJson<MineProblem>(`${one(slug)}review/`, {}),
  tests: (slug: string) => getJson<DraftTest[]>(tests(slug)),
  saveTest: (slug: string, body: DraftTestInput) => postJson<DraftTest>(tests(slug), body),
  removeTest: (slug: string, order: number) =>
    deleteJson<void>(`${tests(slug)}${order}/`),
};

/** A slug suggestion from a title: Latin letters, digits and dashes.
 *
 *  Uzbek apostrophes (`o'`, `g'`, `ʻ`) are dropped, not turned into a
 *  dash: `yig'indi` → `yigindi`, as the existing archive spells them. */
export function slugify(title: string): string {
  return title
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/['ʻʼ‘’`]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .slice(0, 100)
    // Trimmed after the cut: a cut can end on a separator.
    .replace(/^-+|-+$/g, "");
}
