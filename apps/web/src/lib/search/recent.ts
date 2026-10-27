/** Recent searches — this device only.
 *
 *  A convenience, not a preference: it is not part of the account and is
 *  never sent anywhere. Storage can be missing or refuse (private window,
 *  blocked site data), and then there simply is no history.
 */

import { pack, unpack } from "@/lib/versioned-storage";

const KEY = "rw:search-recent";
const VERSION = 1;
export const RECENT_LIMIT = 6;

export function readRecent(): string[] {
  try {
    const raw = window.localStorage.getItem(KEY);
    const got = unpack(raw, VERSION);
    // A bare array is the list from before versioning.
    const parsed: unknown =
      got.kind === "current" ? got.data : got.kind === "legacy" ? JSON.parse(got.raw) : [];
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item): item is string => typeof item === "string").slice(0, RECENT_LIMIT);
  } catch {
    return [];
  }
}

/** Puts `query` first; an older copy of it (any letter case) is dropped. */
export function pushRecent(list: string[], query: string): string[] {
  const clean = query.trim();
  if (clean.length < 2) return list;
  const lower = clean.toLowerCase();
  return [clean, ...list.filter((item) => item.toLowerCase() !== lower)].slice(0, RECENT_LIMIT);
}

export function rememberRecent(query: string): string[] {
  const next = pushRecent(readRecent(), query);
  try {
    window.localStorage.setItem(KEY, pack(VERSION, next));
  } catch {
    // No storage — the search itself still works.
  }
  return next;
}

export function clearRecent(): void {
  try {
    window.localStorage.removeItem(KEY);
  } catch {
    // Nothing to clear.
  }
}
