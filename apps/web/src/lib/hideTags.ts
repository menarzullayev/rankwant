"use client";

import { useCallback, useSyncExternalStore } from "react";

/** Mavzu tegi yechim g'oyasini oshkor qiladi — Codeforces shuning uchun
 * yechilmagan masalada teglarni yashirishni taklif qiladi. Bu qurilma
 * sozlamasi: serverga bormaydi, arxiv va filtr paneli uni bo'lishadi. */
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

export function useHideTags(): [boolean, (next: boolean) => void] {
  const hidden = useSyncExternalStore(subscribe, read, () => false);

  const set = useCallback((next: boolean) => {
    try {
      localStorage.setItem(KEY, next ? "1" : "0");
    } catch {
      // Private rejim — sozlama saqlanmaydi, sahifa ishlayveradi.
    }
    window.dispatchEvent(new Event(EVENT));
  }, []);

  return [hidden, set];
}
