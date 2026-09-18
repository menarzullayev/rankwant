"use client";

import { useCallback, useSyncExternalStore } from "react";

import { useSession } from "@/context/SessionContext";
import { announcePrefs } from "@/lib/prefs";

/** Mavzu tegi yechim g'oyasini oshkor qiladi — Codeforces shuning uchun
 * yechilmagan masalada teglarni yashirishni taklif qiladi. Arxiv va filtr
 * paneli uni bo'lishadi.
 *
 * Since ADR-0024 the setting follows the account. `localStorage` holds this
 * device's copy, which is the whole setting for a guest; `PrefsSync` writes a
 * signed-in change to `ui_prefs.problemset.hideTags` and applies the account's
 * value on sign-in. */
const KEY = "rw:hide-tags";
const EVENT = "rw:hide-tags-change";

function subscribe(onChange: () => void) {
  window.addEventListener(EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

function read(): boolean {
  try {
    return localStorage.getItem(KEY) === "1";
  } catch {
    return false;
  }
}

/** This device's value, or `null` if it was never set. */
export function storedHideTags(): boolean | null {
  try {
    const value = localStorage.getItem(KEY);
    return value === null ? null : value === "1";
  } catch {
    return null;
  }
}

/** Store a value on this device and tell every reader on the page. */
export function rememberHideTags(next: boolean): void {
  try {
    localStorage.setItem(KEY, next ? "1" : "0");
  } catch {
    // Private rejim — sozlama saqlanmaydi, sahifa ishlayveradi.
  }
  window.dispatchEvent(new Event(EVENT));
}

export function useHideTags(): [boolean, (next: boolean) => void] {
  const hidden = useSyncExternalStore(subscribe, read, () => false);
  const signedIn = Boolean(useSession().user);

  const set = useCallback(
    (next: boolean) => {
      rememberHideTags(next);
      if (signedIn) announcePrefs({ problemset: { hideTags: next } });
    },
    [signedIn],
  );

  return [hidden, set];
}
