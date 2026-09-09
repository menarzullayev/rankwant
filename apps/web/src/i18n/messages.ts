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
 * Masala MATNLARI tarjima qilinmaydi — muallif tilida qoladi
 * (Codeforces modeli).
 */

import { en } from "./locales/en";
import { es } from "./locales/es";
import { kaa } from "./locales/kaa";
import { kk } from "./locales/kk";
import { ky } from "./locales/ky";
import { ru } from "./locales/ru";
import { tg } from "./locales/tg";
import { tr } from "./locales/tr";
import { uz, type MessageKey } from "./locales/uz";
import { zh } from "./locales/zh";

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

export const messages: Record<Locale, Record<MessageKey, string>> = {
  uz,
  kaa,
  ru,
  en,
  kk,
  ky,
  tg,
  tr,
  zh,
  es,
};

export function isLocale(value: string | undefined): value is Locale {
  return !!value && (LOCALES as readonly string[]).includes(value);
}

export function t(locale: Locale, key: string): string {
  const dict = messages[locale] as Record<string, string> | undefined;
  return (
    dict?.[key] ??
    (messages[DEFAULT_LOCALE] as Record<string, string>)[key] ??
    key
  );
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
