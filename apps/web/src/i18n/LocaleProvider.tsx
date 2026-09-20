"use client";

import { createContext, use, useContext, useEffect } from "react";

import { DEFAULT_LOCALE, evictOtherLocales, hasMessages, type Locale } from "./messages";

const LocaleContext = createContext<Locale>(DEFAULT_LOCALE);
/** Til avtomatik aniqlanganmi — «Avtomatik» variantining belgisi shu.
 *
 *  `locale` doim ANIQ til bo'ladi (`Accept-Language` dan yechilgan),
 *  ya'ni qaysi holatdaligini faqat shu bayroq bildiradi. */
const AutoContext = createContext<boolean>(true);

/** Injects one dictionary file. The promise settles even when the file fails:
 *  the page then shows keys, which beats an error screen. */
function inject(locale: Locale, url: string): Promise<void> {
  return new Promise<void>((resolve) => {
    const script = document.createElement("script");
    script.src = url;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => {
      console.error(`i18n: the "${locale}" dictionary failed to load from ${url}`);
      resolve();
    };
    document.head.appendChild(script);
  });
}

/** Dictionary files being loaded, by LOCALE — not by URL.
 *
 *  ⚠️ The key is the locale, and an entry is dropped the moment its dictionary
 *  is evicted (`keepOnly`). Keyed by URL and never cleared, this cache
 *  contradicted `evictOtherLocales`: the registry lost the dictionary while the
 *  promise stayed resolved, so returning to a language already visited injected
 *  no `<script>`, the registry stayed empty and the page rendered raw keys.
 *  Measured 2026-09-19 on the live stack, with a real mouse and keyboard:
 *  `ru` → `zh` → `es` → back to `zh` left 38 raw keys on screen
 *  (`nav.problems`, `locale.switchLabel`, …) and stayed broken until a reload.
 *
 *  Re-injecting is cheap: the file is served `immutable` for a year, so the
 *  second request is a cache hit. */
const loading = new Map<Locale, { url: string; promise: Promise<void> }>();

/** Loads a dictionary, once per locale and URL. */
function loadDictionary(locale: Locale, url: string): Promise<void> {
  const cached = loading.get(locale);
  if (cached && cached.url === url) return cached.promise;

  const promise = inject(locale, url).then(async () => {
    // A stale `immutable` file can load and register nothing. Refetching once
    // under a new address is the cheap guard; it cannot loop.
    if (typeof window !== "undefined" && !hasMessages(locale)) {
      console.error(`i18n: the "${locale}" dictionary loaded but registered nothing — refetching`);
      await inject(locale, `${url}&retry=1`);
    }
  });

  loading.set(locale, { url, promise });
  return promise;
}

/** Keeps only `keep` in memory — the registry AND the promise cache together.
 *
 *  They must move in step: `evictOtherLocales` drops a dictionary from the
 *  registry, so the promise cache has to drop it too, or the next visit to that
 *  language has nothing left to inject. */
export function keepOnly(keep: Locale): void {
  for (const locale of [...loading.keys()]) {
    if (locale !== keep) loading.delete(locale);
  }
  evictOtherLocales(keep);
}

/** Test helpers — the two caches have to move together; unit tests prove it. */
export function resetDictionaryLoadsForTests(): void {
  loading.clear();
}

export function markDictionaryLoadForTests(locale: Locale, url = `/i18n/${locale}.js`): void {
  loading.set(locale, { url, promise: Promise.resolve() });
}

export function pendingDictionaryLoads(): Locale[] {
  return [...loading.keys()];
}

/** Already-settled thenable — same identity every render that must not suspend.

 *  A fresh `Promise.resolve()` per render would be a new thenable and React
 *  would treat it as a new `use()` input. */
const READY: Promise<void> = Promise.resolve();

/** Dictionary thenable with a STABLE hook input for every render.
 *
 *  Server and a client that already has the locale: `READY`. Client that
 *  still lacks the file: the in-flight `loadDictionary` promise. The hook
 *  COUNT must not change between those cases — wrapping `use()` in
 *  `if (typeof window && !hasMessages)` skipped the hook on the server and
 *  on a fast client, then added it when the `<head>` script lost the race
 *  with hydration. Lighthouse Slow 4G after inline CSS (HTML ~551 KiB)
 *  reproduced React minified #467 (`Update hook called on initial render`)
 *  and dropped Best practices 100 → 96 (measured 2026-09-20, AFTER-08). */
export function dictionaryReady(locale: Locale, url: string): Promise<void> {
  if (typeof window === "undefined" || hasMessages(locale)) {
    return READY;
  }
  return loadDictionary(locale, url);
}

/** Mijoz komponentlari `cookies()` ni o'qiy olmaydi — til yuqoridan beriladi.
 *
 *  The dictionary is not a prop any more: it comes as a separate cached file
 *  (`dictionaryUrl`). The server has every language registered already. In
 *  the browser the file, requested from `<head>`, usually runs before
 *  hydration. When it has not run yet (a slow network, or a language switch
 *  through `router.refresh()`), rendering suspends until it has, so no
 *  component ever draws a raw key. Inside the switch's transition, React
 *  keeps the old page on screen while it waits.
 *
 *  `use(dictionaryReady(…))` is unconditional. A window/`hasMessages` guard
 *  around `use()` is React #467 — see `dictionaryReady`. */
export function LocaleProvider({
  locale,
  dictionaryUrl,
  auto = true,
  children,
}: {
  locale: Locale;
  /** From `dictionaryUrl()` in `messages.server.ts`. */
  dictionaryUrl: string;
  /** Til `Accept-Language` dan aniqlanganmi (ya'ni odam tanlamaganmi). */
  auto?: boolean;
  children: React.ReactNode;
}) {
  use(dictionaryReady(locale, dictionaryUrl));
  useEffect(() => keepOnly(locale), [locale]);
  return (
    <AutoContext.Provider value={auto}>
      <LocaleContext.Provider value={locale}>{children}</LocaleContext.Provider>
    </AutoContext.Provider>
  );
}

export function useLocale(): Locale {
  return useContext(LocaleContext);
}

export function useLocaleAuto(): boolean {
  return useContext(AutoContext);
}
