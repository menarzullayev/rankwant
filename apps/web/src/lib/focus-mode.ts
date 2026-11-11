"use client";

import { useSyncExternalStore } from "react";

/** Focus mode (decision 2026-11-11 ①): the problem page without the site's
 *  menu, header, banners and footer — the statement and the editor only.
 *
 *  A page-wide switch: `AppShell` reads it to drop its chrome, the problem
 *  page turns it on and off. Not stored: a fresh page starts with the menu,
 *  and leaving the problem page turns it off. */

let focused = false;
const listeners = new Set<() => void>();

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function setFocusMode(on: boolean): void {
  if (focused === on) return;
  focused = on;
  for (const listener of listeners) listener();
}

export function useFocusMode(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => focused,
    () => false,
  );
}
