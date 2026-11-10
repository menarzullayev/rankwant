/** The tabs of one contest's page — a plain module for the same reason as
 *  `editor-tabs.ts`: the server page validates `?tab=` with it. */
export const CONTEST_TABS = ["settings", "problems", "participants"] as const;
export type ContestTab = (typeof CONTEST_TABS)[number];

export const DEFAULT_CONTEST_TAB: ContestTab = CONTEST_TABS[0];

export function contestTab(value: string | undefined): ContestTab {
  return (CONTEST_TABS as readonly string[]).includes(value ?? "")
    ? (value as ContestTab)
    : DEFAULT_CONTEST_TAB;
}
