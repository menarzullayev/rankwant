export const TABS = ["appearance", "a11y"] as const;
export type TabId = (typeof TABS)[number];

/** WAI-ARIA tablist: arrows, Home, and End move and activate the tab. */
export function nextTab(current: TabId, key: string): TabId | null {
  const i = TABS.indexOf(current);
  if (i < 0) return null;
  if (key === "Home") return TABS[0];
  if (key === "End") return TABS[TABS.length - 1];
  if (key === "ArrowRight" || key === "ArrowDown") {
    return TABS[(i + 1) % TABS.length];
  }
  if (key === "ArrowLeft" || key === "ArrowUp") {
    return TABS[(i - 1 + TABS.length) % TABS.length];
  }
  return null;
}
