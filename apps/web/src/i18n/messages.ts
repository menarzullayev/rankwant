/** UI tillari — PRD P0-7.
 *
 * Asosiy to'rtlik: o'zbek, qoraqalpoq, rus, ingliz. Qolganlari mintaqa
 * (qozoq, qirg'iz, tojik, turk) va keng qamrov (xitoy, ispan) uchun.
 *
 * TO'LIQLIK TIPLAR BILAN KAFOLATLANADI: `uz` — manba, qolgan har bir
 * lug'at `Record<MessageKey, string>` sifatida e'lon qilingan, ya'ni
 * bitta kalit tushib qolsa `tsc` yiqiladi. `tools/check_i18n.py` shu
 * kafolatni CI da ham, bo'sh satrlar bilan birga tekshiradi.
 *
 * LUG'ATLAR BU YERDA IMPORT QILINMAYDI — va bu ataylab. Ilgari o'ntasi
 * ham statik import qilinardi; `t()` esa mijoz komponentlaridan
 * chaqiriladi, ya'ni BUTUN jadval har bir tashrifchining JS to'plamiga
 * tushardi. O'lchandi: 312 kB, holbuki bitta til uchun 34 kB yetadi —
 * Slow 4G da o'sha fayl 2.4 s yuklanardi.
 *
 * The server registers every language (`messages.server.ts`). The browser
 * gets only the active one, as a separate cached file
 * (`app/i18n/[file]/route.ts`), not inside the page: it used to be 72 kB of
 * every page's HTML and a third of the render CPU (2026-09-18 profile).
 *
 * Masala MATNLARI tarjima qilinmaydi — muallif tilida qoladi
 * (Codeforces modeli).
 */

import type { MessageKey } from "./locales/uz";

export type { MessageKey };

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

/** Til tanlash ro'yxatida ko'rinadigan nom — HAR DOIM o'sha tilda. */
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

/** Every dictionary this JS realm knows, by locale.
 *
 *  It lives on `globalThis`, not in the module. On the server Next.js
 *  evaluates this module twice: once for server components and once for
 *  client components rendered to HTML. Both must see what
 *  `messages.server.ts` registers, or client components render raw keys
 *  (measured on 2026-09-18). In the browser the dictionary file creates the
 *  same map, whether it runs before or after the app code. */
type Registry = Map<Locale, Record<string, string>>;
const realm = globalThis as typeof globalThis & { __rwMessages?: Registry };
const registry: Registry = (realm.__rwMessages ??= new Map());

/** Properties `translate()` has already logged as missing.
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
export function registerMessages(locale: Locale, dict: Record<MessageKey, string>): void {
  registry.set(locale, dict);
}

/** Whether the dictionary of `locale` is loaded in this realm. */
export function hasMessages(locale: Locale): boolean {
  return registry.has(locale);
}

/** Keeps only `keep` in memory: the browser shows one language at a time,
 *  and each dictionary is ~70 kB. Never on the server, where the registry
 *  holds every language for every request. */
export function evictOtherLocales(keep: Locale): void {
  if (typeof window === "undefined") return;
  for (const locale of registry.keys()) {
    if (locale !== keep) registry.delete(locale);
  }
}

/** Ro'yxatdagi lug'atlar soni — takroriy ro'yxatga olishni o'lchash uchun.
 *
 *  Bu ATAYLAB eksport qilinadi: «xotira o'smaydi» degan da'vo faqat
 *  o'lchov bilan isbotlanadi, o'lchash uchun esa ko'rinish kerak. */
export function registrySize(): number {
  return registry.size;
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

/** Content-name row stored as three language columns.
 *
 *  UI chrome is translated in all ten locales. Topic/skill *content*
 *  still has `name_uz` / `name_ru` / `name_en` only. A locale without a
 *  column must not inherit another language — the English property
 *  (the slug, or `name`) is shown instead.
 */
type Named = {
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

/** Name in `locale`, or the property if that language has no text. */
export function localName(row: Named, locale: Locale): string {
  return localNameInfo(row, locale).text;
}

export function topicName(
  topic: Named & { slug: string },
  locale: Locale,
): string {
  return topicNameInfo(topic, locale).text;
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

export function localNameInfo(row: Named, locale: Locale): NameInfo {
  return nameInfo(row, locale);
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
