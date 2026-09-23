/**
 * Locale identity and dictionary registry — the shared i18n core.
 *
 * WHY THIS LIVES IN `packages/shared`: the rules below (which languages
 * exist, how a missing string is handled, how a dictionary is registered)
 * are *product* decisions, not browser decisions. `apps/web` renders them;
 * a future notification worker or the Go judge's report writer would need
 * the same list and the same lookup contract. Keeping them in `apps/web`
 * meant the rules could only be used by code that also pulled in React.
 *
 * WHAT IS *NOT* HERE: the dictionaries themselves. `apps/web` imports them
 * statically per-locale and registers them
 * (`apps/web/src/i18n/messages.ts`). The package holds the mechanism; the
 * app holds the data. That split is what keeps this package free of a
 * 400 kB dependency on ten translation tables.
 */

/** The ten UI languages — PRD P0-7.
 *
 *  Core four: Uzbek, Karakalpak, Russian, English. The rest cover the
 *  region (Kazakh, Kyrgyz, Tajik, Turkish) and broad reach (Chinese,
 *  Spanish).
 */
export const LOCALES = [
  "uz",
  "kaa",
  "ru",
  "en",
  "kk",
  "ky",
  "tg",
  "tr",
  "zh",
  "es",
] as const;

export type Locale = (typeof LOCALES)[number];

export const DEFAULT_LOCALE: Locale = "uz";

/** Language names for the switcher — ALWAYS in that language.
 *
 *  Endonyms: a Turkish speaker looking for their language scans for
 *  "Türkçe", not "Turkcha". */
export const LOCALE_NAMES: Record<Locale, string> = {
  uz: "O'zbekcha",
  kaa: "Qaraqalpaqsha",
  ru: "Русский",
  en: "English",
  kk: "Қазақша",
  ky: "Кыргызча",
  tg: "Тоҷикӣ",
  tr: "Türkçe",
  zh: "中文",
  es: "Español",
};

/** A message key, derived from the source dictionary by the app. */
export type MessageKey = string;

/** One registered dictionary: key → text. */
export type Dictionary = Record<string, string>;

/** Every dictionary this JS realm knows, by locale.
 *
 *  ⚠️ It lives on `globalThis`, not in the module. On the server Next.js
 *  evaluates this module twice: once for server components and once for
 *  client components rendered to HTML. Both must see what
 *  `messages.server.ts` registers, or client components render raw keys
 *  (measured on 2026-09-18). In the browser the dictionary file creates the
 *  same map, whether it runs before or after the app code.
 *
 *  ⚠️ This is why the extraction to `packages/` had to keep the realm trick:
 *  a plain module-local `Map` here looks correct, passes unit tests, and
 *  silently breaks SSR — the failure mode is "the page shows `nav.contests`",
 *  which no type checker can see. `tools/check_i18n.py` pins it.
 */
type Registry = Map<Locale, Dictionary>;
const realm = globalThis as typeof globalThis & { __rwMessages?: Registry };
const registry: Registry = (realm.__rwMessages ??= new Map());

/** Properties already reported missing, so the console is not flooded.
 *
 *  The log must not fill up: one missing property is looked up on every
 *  row and every render. Repeating `console.error` buries the real fault.
 *  Each property is written once. */
const reported = new Set<string>();

/** Registers one dictionary. It never clears the others.
 *
 *  The server needs all ten at once, and the registry is shared by every
 *  request in the process. A `clear()` here once left only the last language
 *  registered, and the first SSR paint showed dozens of raw keys
 *  (`home.start`, `nav.contests`, …). In the browser, `evictOtherLocales`
 *  drops the languages that are no longer shown.
 */
export function registerMessages(locale: Locale, dict: Dictionary): void {
  registry.set(locale, dict);
}

/** Whether the dictionary of `locale` is loaded in this realm. */
export function hasMessages(locale: Locale): boolean {
  return registry.has(locale);
}

/** Keeps only `keep` in memory: the browser shows one language at a time,
 *  and each dictionary is ~70 kB. Never on the server, where the registry
 *  holds every language for every request.
 *
 *  ⚠️ `typeof window` is the ONE deliberate DOM check in this package. It
 *  is not a feature test — it is the eviction policy itself: "on the client,
 *  drop the others". A worker has no `window` and must keep every language,
 *  which is exactly the behaviour we want there too.
 */
export function evictOtherLocales(keep: Locale): void {
  if (typeof window === "undefined") return;
  for (const locale of registry.keys()) {
    if (locale !== keep) registry.delete(locale);
  }
}

/** How many dictionaries are registered — to measure repeated registration.
 *
 *  This is exported DELIBERATELY: "memory does not grow" is a claim that
 *  can only be proven by measurement, and measuring needs visibility.
 */
export function registrySize(): number {
  return registry.size;
}

/** Empties the registry. FOR TESTS ONLY — the app must never call this.
 *
 *  ⚠️ Nega nomi `reset` va nega ogohlantirish: reyestr `globalThis` da
 *  yashaydi, ya'ni bu chaqiruv SERVERDA barcha so'rovlarning lug'atini
 *  o'chiradi. Ilgari shunaqa `clear()` bo'lgan va birinchi SSR chizig'i
 *  o'nlab xom kalitni ko'rsatgan. `tools/check_i18n.py` `messages.ts` da
 *  bunday chaqiruvni taqiqlaydi; bu funksiya faqat test nusxasi uchun.
 */
export function resetRegistry(): void {
  registry.clear();
  reported.clear();
}

export function isLocale(value: string | null | undefined): value is Locale {
  return !!value && (LOCALES as readonly string[]).includes(value);
}

/** Missing-dictionary behaviour: throw in development, show the property
 *  name in production.
 *
 *  Both sides are deliberate. Silent fallback in development hid bugs
 *  twice (the panel showed raw properties while every check stayed
 *  green). Crashing the page in production blocks the user entirely.
 *
 *  There is no fallback locale. A missing string in `ru` is not replaced
 *  by Uzbek or English — the English property name itself is what the
 *  user sees (`user.name`, `error.invalid`).
 */
const DEV = process.env.NODE_ENV !== "production";

/** One property in one locale. Never reads another locale's dictionary. */
function lookupProperty(locale: Locale, property: string): string {
  const hit = registry.get(locale)?.[property];
  if (hit !== undefined && hit !== "") {
    reported.delete(`${locale}:${property}`);
    return hit;
  }

  const hasDict = registry.has(locale);
  const detail = hasDict
    ? `property "${property}" missing from the "${locale}" dictionary`
    : `dictionary for locale "${locale}" is not registered`;

  if (DEV) {
    throw new Error(`i18n: ${detail}`);
  }

  const tag = `${locale}:${property}`;
  if (!reported.has(tag)) {
    reported.add(tag);
    console.error(`i18n: ${detail} — rendering the property name instead`);
  }

  return property;
}

/** Translate English property names (`user.name`, `error.invalid`).
 *
 *  One property → that string. Several properties → an array, same
 *  order. A missing translation is the property name itself; no other
 *  language is consulted.
 */
export function translate(locale: Locale, property: string): string;
export function translate(locale: Locale, ...properties: string[]): string[];
export function translate(
  locale: Locale,
  ...properties: string[]
): string | string[] {
  const texts = properties.map((property) => lookupProperty(locale, property));
  return properties.length === 1 ? texts[0]! : texts;
}

/** Single-property shortcut used throughout the UI. Same contract as
 *  `translate(locale, property)`. */
export function t(locale: Locale, property: string): string {
  return translate(locale, property);
}

/** `{nom}` o'rinlarini qiymat bilan to'ldiradi: `fill("{n} ta", { n: 3 })`. */
export function fill(
  text: string,
  values: Record<string, string | number>,
): string {
  return text.replace(/\{(\w+)\}/g, (whole, key: string) =>
    key in values ? String(values[key]) : whole,
  );
}

/** Tag to pass to `Intl`. Never substitutes another language.
 *
 *  ICU silently maps some tags (`kaa`, `ky`, `tg`) to `en-US`. We still
 *  return the requested tag so date formatting does not jump to Uzbek.
 */
export function intlLocale(locale: Locale): string {
  return locale;
}

/** Sana-vaqtni tilga mos ko'rinishda. Qarang: `intlLocale`. */
export function dateTime(
  value: string | number | Date,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions,
): string {
  return new Date(value).toLocaleString(intlLocale(locale), options);
}

/** Faqat sana (vaqtsiz) — qarang: `intlLocale`. */
export function date(
  value: string | number | Date,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions,
): string {
  return new Date(value).toLocaleDateString(intlLocale(locale), options);
}

/** Faqat vaqt (sanasiz) — qarang: `intlLocale`. */
export function time(
  value: string | number | Date,
  locale: Locale,
  options?: Intl.DateTimeFormatOptions,
): string {
  return new Date(value).toLocaleTimeString(intlLocale(locale), options);
}

/** Content names that have a dedicated column.
 *
 *  UI chrome is in all ten locales. Topic/skill *content* still lives
 *  in `name_uz` / `name_ru` / `name_en`. Other locales must not inherit
 *  Uzbek — they show the English property (the slug) instead.
 */
export const CONTENT_NAME_LOCALES = ["uz", "ru", "en"] as const;

/** Whether `locale` has a content-name column. */
export function hasContentNames(locale: Locale): boolean {
  return (CONTENT_NAME_LOCALES as readonly string[]).includes(locale);
}

// ── Content names: rows that carry only three language columns ──────────

/** Content-name row stored as three language columns.
 *
 *  UI chrome is translated in all ten locales. Topic/skill *content*
 *  still has `name_uz` / `name_ru` / `name_en` only. A locale without a
 *  column must not inherit another language — the English property
 *  (the slug, or `name`) is shown instead.
 */
export type Named = {
  name_uz: string;
  name_ru: string;
  name_en: string;
  slug?: string;
};

function columnFor(row: Named, locale: Locale): string {
  if (locale === "uz") return row.name_uz;
  if (locale === "ru") return row.name_ru;
  if (locale === "en") return row.name_en;
  return "";
}

/** Property shown when the requested language has no name. */
function nameProperty(row: Named): string {
  return row.slug || "name";
}

/** Name plus whether it is a real translation in `locale`.
 *
 *  `locale === null` means the requested language has no text — `text`
 *  is the English property, not a silent copy of another language.
 */
export type NameInfo = {
  text: string;
  locale: Locale | null;
  source: Locale | null;
};

function nameInfo(row: Named, locale: Locale): NameInfo {
  const text = columnFor(row, locale).trim();
  if (text) return { text, locale, source: locale };
  return { text: nameProperty(row), locale: null, source: null };
}

/** Name in `locale`, or the property if that language has no text. */
export function localName(row: Named, locale: Locale): string {
  return localNameInfo(row, locale).text;
}

export function localNameInfo(row: Named, locale: Locale): NameInfo {
  return nameInfo(row, locale);
}

export function topicName(
  topic: Named & { slug: string },
  locale: Locale,
): string {
  return topicNameInfo(topic, locale).text;
}

export function topicNameInfo(
  topic: Named & { slug: string },
  locale: Locale,
): NameInfo {
  return nameInfo(topic, locale);
}

/** API error `code` → `error.<code>` property.
 *
 *  The server message is ignored: it must not stand in for a missing
 *  translation. A code without a dictionary entry renders as `error.<code>`.
 */
export function errorText(
  locale: Locale,
  code: string,
  _serverMessage?: string,
): string {
  const property = code ? `error.${code}` : "error.error";
  return translate(locale, property);
}
