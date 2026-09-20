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

/** Sitemap `xhtml:link` — har resurs bitta `<url>`, tillar `alternates`.
 *
 *  `url` toza `uz` yo'l (HITL sitemap-hreflang). 10× alohida `<url>` yo'q.
 */
export function sitemapLanguageAlternates(
  path: string,
  toAbsolute: (href: string) => string,
): Record<string, string> {
  const { languages } = localeAlternates(path, null);
  const out: Record<string, string> = {};
  for (const [code, href] of Object.entries(languages)) {
    out[code] = toAbsolute(href);
  }
  return out;
}
