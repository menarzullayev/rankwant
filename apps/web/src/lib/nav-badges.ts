/** Side-menu badges — the part with no React in it (see `NavBadgesContext`). */

export type NavBadgeKind = "todo" | "live" | "unread" | "new";

export type NavBadgeView = { kind: NavBadgeKind; count: number };

/** Keyed by the menu entry's path: `/duels`, `/blog`. */
export type NavBadgeMap = Record<string, NavBadgeView>;

const KINDS: ReadonlySet<string> = new Set(["todo", "live", "unread", "new"]);

/** Sections whose badge means "published since you were last here":
 *  opening the list is what clears it. `todo` and `live` are not here —
 *  they follow the work and the clock, not a visit. */
export const SEEN_ON_VISIT: ReadonlySet<string> = new Set([
  "blog",
  "problems",
  "learn",
  "algorithms",
  "quizzes",
]);

/** `/blog` → `blog`. Only the list itself counts as opening a section:
 *  reading one post does not mean the others were seen. */
export function sectionOf(pathname: string): string | null {
  const match = /^\/([a-z-]+)\/?$/.exec(pathname);
  return match ? match[1] : null;
}

/** The server's rows plus the changelog's own count, keyed by path.
 *  A kind this build does not know is dropped rather than drawn wrong. */
export function toBadgeMap(
  rows: readonly { section: string; kind: string; count: number }[],
  updates: number,
): NavBadgeMap {
  const map: NavBadgeMap = {};
  for (const row of rows) {
    if (!KINDS.has(row.kind) || row.count <= 0) continue;
    map[`/${row.section}`] = {
      kind: row.kind as NavBadgeKind,
      count: row.count,
    };
  }
  if (updates > 0) map["/updates"] = { kind: "unread", count: updates };
  return map;
}

/** What the chip prints. A live section shows a word, never a number. */
export function badgeText(count: number): string {
  return count > 99 ? "99+" : String(count);
}
