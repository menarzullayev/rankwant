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
 * Endi faqat AKTIV tilning lug'ati yuboriladi: SSR da uni
 * `messages.server.ts` ro'yxatga oladi, brauzerda esa `layout.tsx`
 * chiqargan inline skript (xuddi `THEME_INIT`/`STYLE_INIT` kabi).
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

/** Aktiv tilning lug'ati.
 *
 *  Faqat BITTA yozuv bo'ladi: SSR da uni `messages.server.ts` to'ldiradi,
 *  brauzerda esa quyidagi inline-skript o'quvchi qism. Ilgari bu yerda
 *  o'nta tilning hammasi turardi. */
const registry = new Map<string, Record<string, string>>();

/** Lug'atni ro'yxatga oladi. Amalda faqat aktiv til uchun chaqiriladi. */
export function registerMessages(locale: Locale, dict: Record<MessageKey, string>): void {
  registry.set(locale, dict);
}

export function isLocale(value: string | undefined): value is Locale {
  return !!value && (LOCALES as readonly string[]).includes(value);
}

export function t(locale: Locale, key: string): string {
  // Zaxira `uz` EMAS: u ham yuborilmaydi. To'liqlikni tip
  // (`Record<MessageKey, string>`) va `tools/check_i18n.py` kafolatlaydi,
  // ya'ni lug'atda kalit yetishmay qolmaydi — `key` ga tushish faqat
  // `MessageKey` bo'lmagan satr uchun bo'ladi.
  return registry.get(locale)?.[key] ?? key;
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

/** Uch ustunli nom (ko'nikma, mavzu, vazifa) — tilga mosi, bo'lmasa o'zbekchasi. */
export function localName(
  row: { name_uz: string; name_ru: string; name_en: string },
  locale: Locale,
): string {
  const translated =
    locale === "ru" ? row.name_ru : locale === "en" ? row.name_en : "";
  return translated || row.name_uz;
}

/** Mavzu nomi — bazada faqat uz/ru/en ustunlari bor.
 *
 * UI satrlari o'nta tilda, mavzu nomlari esa uchta ustunda: ular
 * KONTENT, ya'ni ularni tarjima qilish alohida ish (145 ta mavzu).
 * Ustuni yo'q yoki bo'sh til uchun o'zbekchasiga qaytamiz — bo'sh
 * yorliq ko'rsatishdan ko'ra tushunarli.
 */
export function topicName(
  topic: { slug: string; name_uz: string; name_ru: string; name_en: string },
  locale: Locale,
): string {
  const translated =
    locale === "ru" ? topic.name_ru : locale === "en" ? topic.name_en : "";
  return translated || topic.name_uz || topic.slug;
}

/** API xatosining matni — kod bo'yicha, server matni zaxira sifatida.
 *
 * API barqaror `code` beradi (`08-technical-spec` xato formati), matn
 * esa o'zbekcha keladi: `LocaleMiddleware` va `USE_I18N` yoqilgan, lekin
 * `locale/` katalogi yo'q va birorta ham `gettext` chaqiruvi yo'q —
 * o'lchandi. Kodni shu yerda tarjima qilish gettext'dan yaxshiroq:
 * bitta tarjima tizimi, `.po` fayllarsiz va qurish quroli talab
 * qilmasdan.
 *
 * Tanilmagan kod uchun server matni ko'rsatiladi — bo'sh joydan yaxshi.
 */
export function errorText(
  locale: Locale,
  code: string,
  fallback: string,
): string {
  const key = `error.${code}`;
  return registry.get(locale)?.[key] ?? fallback ?? t(locale, "error.error");
}
