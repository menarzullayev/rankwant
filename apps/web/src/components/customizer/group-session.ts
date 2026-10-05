import { GROUPS, type GroupId } from "./chrome";

/** D65: last open accordion — this tab's session only, not the account. */
export const GROUP_SESSION_KEY = "rw:cz-group";
export const DEFAULT_GROUP: GroupId = "look";

export function clampGroup(value: unknown): GroupId {
  return GROUPS.includes(value as GroupId) ? (value as GroupId) : DEFAULT_GROUP;
}

/** Stored when the visitor closes the open group: every group is shut. */
const CLOSED = "none";

const listeners = new Set<() => void>();
// A new tab starts with every group closed: the quick row and the
// templates above them are the first screen (2026-10-05).
let memory: GroupId | null = null;

export function subscribeGroup(onChange: () => void) {
  listeners.add(onChange);
  return () => {
    listeners.delete(onChange);
  };
}

export function readGroup(): GroupId | null {
  try {
    const raw = sessionStorage.getItem(GROUP_SESSION_KEY);
    if (raw === null) return memory;
    return raw === CLOSED ? null : clampGroup(raw);
  } catch {
    return memory;
  }
}

export function writeGroup(id: GroupId | null) {
  const next = id === null ? null : clampGroup(id);
  memory = next;
  try {
    sessionStorage.setItem(GROUP_SESSION_KEY, next ?? CLOSED);
  } catch {
    // Private mode — `memory` still updates this tab.
  }
  for (const listener of listeners) listener();
}
