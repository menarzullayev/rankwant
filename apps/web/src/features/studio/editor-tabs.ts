/** The tabs of one draft's page. A plain module, not the editor's: the
 *  server page reads this list to validate `?tab=`, and a value exported
 *  from a `"use client"` file reaches the server only as a reference
 *  (`EDITOR_TABS.includes is not a function`, measured 2026-11-10). */
export const EDITOR_TABS = ["statement", "tests", "editorial", "review"] as const;
export type EditorTab = (typeof EDITOR_TABS)[number];

/** The tab a bare URL opens — also the only tab of a new draft. */
export const DEFAULT_TAB: EditorTab = EDITOR_TABS[0];

export function editorTab(value: string | undefined): EditorTab {
  return (EDITOR_TABS as readonly string[]).includes(value ?? "") ? (value as EditorTab) : DEFAULT_TAB;
}
