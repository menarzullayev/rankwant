import { TABS, type TabId } from "./tabs";

/** D66: last open tab — this tab's session only, not the account. */
export const TAB_SESSION_KEY = "rw:cz-tab";
export const DEFAULT_TAB: TabId = "appearance";

export function clampTab(value: unknown): TabId {
  return TABS.includes(value as TabId) ? (value as TabId) : DEFAULT_TAB;
}

const listeners = new Set<() => void>();
let memory: TabId = DEFAULT_TAB;

export function subscribeTab(onChange: () => void) {
  listeners.add(onChange);
  return () => {
    listeners.delete(onChange);
  };
}

export function readTab(): TabId {
  try {
    return clampTab(sessionStorage.getItem(TAB_SESSION_KEY) ?? memory);
  } catch {
    return memory;
  }
}

export function writeTab(id: TabId) {
  const next = clampTab(id);
  memory = next;
  try {
    sessionStorage.setItem(TAB_SESSION_KEY, next);
  } catch {
    // Private mode — `memory` still updates this tab.
  }
  for (const listener of listeners) listener();
}
