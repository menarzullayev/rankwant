import { LOCALE_PARAM } from "./locale-params";
import { DEFAULT_LOCALE, LOCALES, isLocale, type Locale } from "./messages";

/** `?lang=` self-canonical + hreflang (HITL 2026-09-20).
 *
 *  Filtr query (`?contest=`) canonical'ga kirmaydi. `uz` — toza yo'l
 *  (`/?lang=uz` → `/`); boshqa til — `?lang=` o'ziga canonical.
 *  CDN keshi `?lang=` ni baribir chiqaradi (`home-cache.ts`).
 */

export function hrefForLocale(path: string, locale: Locale): string {
  if (locale === DEFAULT_LOCALE) return path;
  return `${path}?${LOCALE_PARAM}=${locale}`;
}

export function localeAlternates(
  path: string,
  langParam: string | null,
): { canonical: string; languages: Record<string, string> } {
  const canonical =
    isLocale(langParam) && langParam !== DEFAULT_LOCALE
      ? hrefForLocale(path, langParam)
      : path;
  const languages: Record<string, string> = { "x-default": path };
  for (const locale of LOCALES) {
    languages[locale] = hrefForLocale(path, locale);
  }
  return { canonical, languages };
}
