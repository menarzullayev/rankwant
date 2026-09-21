import { GROUPS, type GroupId } from "./chrome";

/** D65: last open accordion — this tab's session only, not the account. */
export const GROUP_SESSION_KEY = "rw:cz-group";
export const DEFAULT_GROUP: GroupId = "look";

export function clampGroup(value: unknown): GroupId {
  return GROUPS.includes(value as GroupId) ? (value as GroupId) : DEFAULT_GROUP;
}

const listeners = new Set<() => void>();
let memory: GroupId = DEFAULT_GROUP;

export function subscribeGroup(onChange: () => void) {
  listeners.add(onChange);
  return () => {
    listeners.delete(onChange);
  };
}

export function readGroup(): GroupId {
  try {
    return clampGroup(sessionStorage.getItem(GROUP_SESSION_KEY) ?? memory);
  } catch {
    return memory;
  }
}

export function writeGroup(id: GroupId) {
  const next = clampGroup(id);
  memory = next;
  try {
    sessionStorage.setItem(GROUP_SESSION_KEY, next);
  } catch {
    // Private mode — `memory` still updates this tab.
  }
  for (const listener of listeners) listener();
}
