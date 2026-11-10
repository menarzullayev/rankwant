/** `/studio/contests` — the organizer's own contests (ADR-0025, 2026-11-10).
 *
 *  One API surface: `contests/mine/` — the contest, its problems (only the
 *  organizer's own unpublished ones, only while the contest is a draft) and
 *  the people registered for it.
 */

import { SITE_TZ } from "@rankwant/shared/format";

import {
  deleteJson,
  getJson,
  patchJson,
  postJson,
  putJson,
  type Paginated,
} from "@/lib/api/client";

/** `contests.organizer_views.MAX_DRAFTS` — the rule `studio_contests_panel`
 *  keeps the two equal. */
export const STUDIO_CONTEST_LIMIT = 5;

export type ContestScoring = "acm" | "ioi";

export type MineContestProblem = {
  problem: string;
  index_letter: string;
  points: number;
  title: string;
};

export type MineContest = {
  slug: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  freeze_minutes: number;
  scoring_type: ContestScoring;
  is_public: boolean;
  is_rated: boolean;
  testers: string[];
  problems: MineContestProblem[];
  participant_count: number;
};

export type MineContestInput = Partial<
  Pick<
    MineContest,
    | "slug"
    | "title"
    | "description"
    | "start_at"
    | "end_at"
    | "freeze_minutes"
    | "scoring_type"
    | "testers"
  >
>;

export type ContestParticipant = {
  username: string;
  display_name: string;
  registered_at: string;
};

const MINE = "/contests/mine/";
const one = (slug: string) => `${MINE}${encodeURIComponent(slug)}/`;

export const studioContests = {
  list: () => getJson<Paginated<MineContest>>(MINE),
  create: (body: MineContestInput) => postJson<MineContest>(MINE, body),
  update: (slug: string, body: MineContestInput) => patchJson<MineContest>(one(slug), body),
  remove: (slug: string) => deleteJson<void>(one(slug)),
  setProblems: (slug: string, problems: { problem: string; index_letter: string; points: number }[]) =>
    putJson<MineContestProblem[]>(`${one(slug)}problems/`, { problems }),
  participants: (slug: string) => getJson<ContestParticipant[]>(`${one(slug)}participants/`),
};

/** Problem letters in order: A, B, … Z. A contest past 26 problems is not
 *  something an organizer drafts here. */
export function letterAt(index: number): string {
  return String.fromCharCode(65 + index);
}

const INPUT_PARTS = new Intl.DateTimeFormat("en-GB", {
  timeZone: SITE_TZ,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

/** A moment as a `datetime-local` value in the SITE zone (Asia/Tashkent).
 *
 *  Not the browser's zone: a contest starts at one moment for everybody,
 *  and every other date on the site is written in Tashkent time — an
 *  organizer abroad would otherwise schedule it hours off. */
export function toSiteInput(iso: string): string {
  const parts = Object.fromEntries(
    INPUT_PARTS.formatToParts(new Date(iso)).map((part) => [part.type, part.value]),
  );
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`;
}

/** Asia/Tashkent is UTC+5 all year (no daylight saving since 1992). */
const SITE_OFFSET = "+05:00";

/** A `datetime-local` value read as site time, as an ISO moment. */
export function fromSiteInput(value: string): string {
  return new Date(`${value}:00${SITE_OFFSET}`).toISOString();
}

/** Comma- or space-separated usernames → a clean list, `@` dropped. */
export function parseUsernames(text: string): string[] {
  return [
    ...new Set(
      text
        .split(/[\s,]+/)
        .map((name) => name.replace(/^@/, "").trim())
        .filter(Boolean),
    ),
  ];
}
