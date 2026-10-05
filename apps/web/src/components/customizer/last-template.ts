import { TEMPLATES, type Template } from "@/lib/theme/templates";

/** The team template applied last in this tab — so "modified" can offer
 *  the way back. Session only, like the open group (D65) and the open tab
 *  (D66): it is the panel's memory, not an account preference. */
export const LAST_TEMPLATE_KEY = "rw:cz-template";

const listeners = new Set<() => void>();
let memory: string | null = null;

export function subscribeLastTemplate(onChange: () => void) {
  listeners.add(onChange);
  return () => {
    listeners.delete(onChange);
  };
}

/** The id only: a snapshot has to be a stable value between renders. */
export function readLastTemplateId(): string | null {
  try {
    return sessionStorage.getItem(LAST_TEMPLATE_KEY) ?? memory;
  } catch {
    return memory;
  }
}

/** An id that no longer names a template yields nothing, not a crash. */
export function findTemplate(id: string | null): Template | null {
  return TEMPLATES.find((item) => item.id === id) ?? null;
}

export function writeLastTemplate(id: string) {
  memory = id;
  try {
    sessionStorage.setItem(LAST_TEMPLATE_KEY, id);
  } catch {
    // Private mode — `memory` still serves this tab.
  }
  for (const listener of listeners) listener();
}
