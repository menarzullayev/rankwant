"use client";

import { createContext, use, useContext, useEffect } from "react";

import { DEFAULT_LOCALE, evictOtherLocales, hasMessages, type Locale } from "./messages";

const LocaleContext = createContext<Locale>(DEFAULT_LOCALE);
/** Til avtomatik aniqlanganmi — «Avtomatik» variantining belgisi shu.
 *
 *  `locale` doim ANIQ til bo'ladi (`Accept-Language` dan yechilgan),
 *  ya'ni qaysi holatdaligini faqat shu bayroq bildiradi. */
const AutoContext = createContext<boolean>(true);

/** Dictionary files being loaded, by URL: each loads once. */
const loading = new Map<string, Promise<void>>();

/** Loads a dictionary file. The promise settles even when the file fails:
 *  the page then shows keys, which beats an error screen. */
function loadDictionary(locale: Locale, url: string): Promise<void> {
  let promise = loading.get(url);
  if (!promise) {
    promise = new Promise<void>((resolve) => {
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
    loading.set(url, promise);
  }
  return promise;
}

/** Mijoz komponentlari `cookies()` ni o'qiy olmaydi — til yuqoridan beriladi.
 *
 *  The dictionary is not a prop any more: it comes as a separate cached file
 *  (`dictionaryUrl`). The server has every language registered already. In
 *  the browser the file, requested from `<head>`, usually runs before
 *  hydration. When it has not run yet (a slow network, or a language switch
 *  through `router.refresh()`), rendering suspends until it has, so no
 *  component ever draws a raw key. Inside the switch's transition, React
 *  keeps the old page on screen while it waits. */
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
  if (typeof window !== "undefined" && !hasMessages(locale)) {
    use(loadDictionary(locale, dictionaryUrl));
  }
  useEffect(() => evictOtherLocales(locale), [locale]);
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
