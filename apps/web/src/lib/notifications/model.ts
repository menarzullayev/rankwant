/** Notifications — what the bell panel and the full page share. */

import { dateTime, fill, t, time, type Locale } from "@/i18n/messages";

export type Notification = {
  id: number;
  kind: string;
  /** Text in the recipient's language at the time of the event — the fallback. */
  title: string;
  body: string;
  /** What happened, as a key; empty for free text a person wrote. */
  code: string;
  params: Record<string, string | number>;
  ref_type: string;
  ref_id: string;
  is_read: boolean;
  created_at: string;
};

export type NotificationSummary = {
  total: number;
  unread: number;
  /** Unread and not yet shown in the bell — what the badge counts. */
  unseen: number;
  /** Kinds this user has at least one notification of. */
  kinds: string[];
};

export const EMPTY_SUMMARY: NotificationSummary = { total: 0, unread: 0, unseen: 0, kinds: [] };

/** Rows the bell panel shows, and one page of the full list. */
export const PANEL_SIZE = 8;
export const PAGE_SIZE = 20;

/** How long a deletion can still be taken back. */
export const UNDO_MS = 5000;

/** Refresh interval while the live channel is down. */
export const POLL_MS = 60_000;

const STAMP: Intl.DateTimeFormatOptions = {
  // Numeric on purpose: browsers without Uzbek month names print a short
  // month as "M10" (measured 2026-10-05).
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
};
const CLOCK: Intl.DateTimeFormatOptions = { hour: "2-digit", minute: "2-digit" };

/** Values as shown: a key ending in `_at` holds a timestamp. */
function shown(
  params: Notification["params"],
  locale: Locale,
): Record<string, string | number> {
  const out: Record<string, string | number> = {};
  for (const [key, value] of Object.entries(params)) {
    out[key] = key.endsWith("_at") && typeof value === "string" ? dateTime(value, locale, STAMP) : value;
  }
  return out;
}

/** Codes the dictionaries know, and whether each has a body sentence.
 *
 *  Listed rather than probed: a missing key throws in development. A code
 *  without a body here keeps the body stored on the row — a judge's own
 *  feedback, a checker's detail line. `search-model`-style unit tests
 *  compare this table with the dictionary, so the two cannot drift.
 */
export const MESSAGE_CODES: Record<string, { body: boolean }> = {
  duel_accepted: { body: true },
  duel_cancelled: { body: true },
  duel_won: { body: true },
  duel_lost: { body: true },
  duel_draw: { body: true },
  hackathon_scored: { body: false },
  hack_succeeded: { body: false },
  hack_failed: { body: false },
  hack_invalid: { body: false },
  hack_crashed: { body: false },
  hack_ignored: { body: false },
  hack_received: { body: true },
  streak: { body: true },
  problem_rerated: { body: true },
  contest_result: { body: true },
};

/** The words of a notification in the language it is being read in.
 *
 *  A coded row is drawn from the dictionary; free text, and a code this
 *  build does not know (an older client, a retired code), fall back to
 *  the text stored on the row.
 */
export function notificationText(
  row: Notification,
  locale: Locale,
): { title: string; body: string } {
  const known = row.code ? MESSAGE_CODES[row.code] : undefined;
  if (!known) return { title: row.title, body: row.body };
  const values = shown(row.params ?? {}, locale);
  return {
    title: fill(t(locale, `notif.msg.${row.code}.title`), values),
    body: known.body ? fill(t(locale, `notif.msg.${row.code}.body`), values) : row.body,
  };
}

/** Where a notification leads, or `null` when there is nowhere to go. */
export function notificationHref(row: Notification): string | null {
  const id = encodeURIComponent(row.ref_id);
  switch (row.ref_type) {
    case "duel":
      return `/duels/${id}`;
    case "contest":
      return `/contests/${id}`;
    case "problem":
      return `/problems/${id}`;
    case "attempt":
      return `/attempts/${id}`;
    case "hack": {
      // A hack has no page of its own; its problem does.
      const problem = row.params?.problem;
      return typeof problem === "string" ? `/problems/${encodeURIComponent(problem)}` : null;
    }
    case "hackathon":
      return `/hackathons/${id}`;
    case "arena":
      return `/arena/${id}`;
    case "quiz":
      return `/quizzes/${id}`;
    case "post":
      return `/blog/${id}`;
    case "streak":
      return "/qvant";
    case "mail_quota":
      return "/admin/email-quota";
    default:
      return null;
  }
}

const ICONS: Record<string, string> = {
  contest_result: "ranking.trophy",
  rating_changed: "nav.leaderboard",
  problem_rerated: "nav.leaderboard",
  duel: "contest.flag",
  hack: "status.warning",
  quest_awarded: "action.confirm",
  streak_milestone: "ranking.streak",
  system: "notification.bell",
};

export function notificationIcon(kind: string): string {
  return ICONS[kind] ?? "notification.bell";
}

export type DayGroup = "today" | "yesterday" | "earlier";

function dayStart(moment: Date): number {
  return new Date(moment.getFullYear(), moment.getMonth(), moment.getDate()).getTime();
}

/** Which heading a row sits under, by the reader's own calendar day. */
export function dayGroup(createdAt: string, now: Date = new Date()): DayGroup {
  const gap = dayStart(now) - dayStart(new Date(createdAt));
  if (gap <= 0) return "today";
  if (gap <= 86_400_000) return "yesterday";
  return "earlier";
}

/** Today: the time. Any other day: the date and the time. */
export function timeLabel(createdAt: string, locale: Locale, now: Date = new Date()): string {
  return dayGroup(createdAt, now) === "today"
    ? time(createdAt, locale, CLOCK)
    : dateTime(createdAt, locale, STAMP);
}

/** The cursor out of a `next` link — the API's own host is not ours to follow. */
export function cursorOf(next: string | null): string | null {
  if (!next) return null;
  try {
    return new URL(next, "http://x").searchParams.get("cursor");
  } catch {
    return null;
  }
}

export function listQuery(options: {
  unread: boolean;
  kind: string | null;
  size: number;
  cursor?: string | null;
}): string {
  const params = new URLSearchParams({ page_size: String(options.size) });
  if (options.unread) params.set("unread", "true");
  if (options.kind) params.set("kind", options.kind);
  if (options.cursor) params.set("cursor", options.cursor);
  return `?${params.toString()}`;
}
