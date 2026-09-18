import type { ThemeTemplate, UiPrefs } from "@/lib/api";

/** How many saved templates a signed-in user keeps (D21); a guest keeps 2. */
export const SIGNED_IN_TEMPLATE_LIMIT = 5;

/** The account's saved templates joined with this device's, at sign-in
 *  (owner decision 2026-09-18, APP-13).
 *
 *  Names match without regard to case. On a clash the account's copy wins,
 *  because the account is what every other device sees. Templates that
 *  exist only on this device follow, and the list is cut at `limit` with
 *  the account's kept first. Before this, a new device never loaded the
 *  account's list, and its first change sent an empty list that wiped it.
 *
 *  `CustomizerProvider` shows the result and `PrefsSync` stores it. Both
 *  call this with the same two lists, so they agree without talking. */
export function mergeSavedTemplates(
  account: ThemeTemplate[],
  device: ThemeTemplate[],
  limit: number,
): ThemeTemplate[] {
  const taken = new Set(account.map((row) => row.name.toLowerCase()));
  const extra = device.filter((row) => !taken.has(row.name.toLowerCase()));
  return [...account, ...extra].slice(0, limit);
}

/** The saved templates stored in an account's `ui_prefs`, or none. */
export function accountTemplates(prefs: UiPrefs | null | undefined): ThemeTemplate[] {
  return Array.isArray(prefs?.templates) ? prefs.templates : [];
}
