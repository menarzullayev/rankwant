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
const registry = new Map<Locale, Record<string, string>>();

/** `t()` allaqachon shikoyat qilgan kalitlar.
 *
 *  Jurnal TO'LDIRILMAYDI: bitta yetishmagan kalit yuzlab marta chaqiriladi
 *  (har ro'yxat qatori, har chizish) — takroriy `console.error` haqiqiy
 *  xatoni ko'mib tashlaydi. Shuning uchun har kalit BIR MARTA yoziladi. */
const reported = new Set<string>();

/** Lug'atni ro'yxatga oladi.
 *
 *  ⚠️ CHEGARA ikki xil, va bu ATAYLAB:
 *
 *  * **Serverda** o'nta lug'atning HAMMASI kerak: `layout.tsx` aktiv
 *    tilni aniqlaydi, lekin sahifalar `messages.server.ts` modul
 *    yuklanishida ro'yxatga olinadi — ya'ni har bir til uchun `t()`
 *    ishlashi shart. Ilgari bu yerda `registry.clear()` bor edi va
 *    modul yuklanishidagi tsikl faqat OXIRGI tilni (`es`) qoldirardi;
 *    natijada birinchi SSR chizishida o'nlab xom kalit chiqardi
 *    (`home.start`, `nav.contests`, …) — o'lchandi, brauzerda.
 *  * **Klientda** faqat aktiv til kerak: `LocaleProvider` bitta lug'at
 *    uzatadi, ya'ni chegaralash xotirani tejaydi (~450 kB → bitta).
 *
 *  Shuning uchun `evict` bayrog'i: serverda `false`, klientda `true`.
 *  Ilgari chegara SHARTSIZ edi — bu jimgina nuqson tug'dirdi.
 */
export function registerMessages(
  locale: Locale,
  dict: Record<MessageKey, string>,
  evict = false,
): void {
  if (evict) {
    // Klientda boshqa tillar kerak emas — bir zarbada tozalaymiz.
    registry.clear();
    reported.clear();
  }
  registry.set(locale, dict);
}

/** Ro'yxatdagi lug'atlar soni — takroriy ro'yxatga olishni o'lchash uchun.
 *
 *  Bu ATAYLAB eksport qilinadi: «xotira o'smaydi» degan da'vo faqat
 *  o'lchov bilan isbotlanadi, o'lchash uchun esa ko'rinish kerak. */
export function registrySize(): number {
  return registry.size;
}

export function isLocale(value: string | undefined): value is Locale {
  return !!value && (LOCALES as readonly string[]).includes(value);
}

/** Lug'at topilmaganda qanday yo'l tutish — dev'da yiqilish, prod'da
 *  ko'rinadigan kalit.
 *
 *  Ikkala holat ham ATaylab: dev'da jim o'tish bugni ishlab chiqish
 *  paytida yashiradi (aynan shu bugun ikki marta bo'ldi — panel ekranda
 *  xom kalitlarni ko'rsatdi, holbuki hamma tekshiruv yashil edi), prod'da
 *  esa sahifani yiqitish foydalanuvchini butunlay to'sadi. */
const DEV = process.env.NODE_ENV !== "production";

/** `t()` uchun bitta kirish nuqtasi — shu sabab `errorText()` ham
 *  aynan bir xil yo'ldan o'tadi va ikki xil xatti-harakat bo'lib
 *  qolmaydi. */
function lookup(locale: Locale, key: string, fallback?: string): string {
  const hit = registry.get(locale)?.[key];
  if (hit !== undefined && hit !== "") {
    reported.delete(`${locale}:${key}`);
    return hit;
  }

  // Zaxira `uz` EMAS: u ham yuborilmaydi (34 kB) va nuqsonni yashiradi.
  // To'liqlikni tip (`Record<MessageKey, string>`) va
  // `tools/check_i18n.py` kafolatlaydi — bu yerga tushish faqat lug'at
  // ro'yxatga olinmagan yoki kalit umuman mavjud bo'lmaganda bo'ladi.
  const hasDict = registry.has(locale);
  const detail = hasDict
    ? `key "${key}" missing from the "${locale}" dictionary`
    : `dictionary for locale "${locale}" is not registered`;

  if (DEV) {
    throw new Error(`i18n: ${detail}`);
  }

  const tag = `${locale}:${key}`;
  if (!reported.has(tag)) {
    reported.add(tag);
    // `console.error` — `warn` emas: bu ekranga noto'g'ri matn chiqishi,
    // ya'ni ishlab turgan mahsulotdagi ko'rinadigan nuqson.
    console.error(`i18n: ${detail} — rendering the key instead`);
  }

  // Fallback bor bo'lsa (server matni, masalan API xatosi) — kalitdan
  // ko'ra o'sha matn foydaliroq.
  return fallback !== undefined && fallback !== "" ? fallback : key;
}

export function t(locale: Locale, key: string): string {
  return lookup(locale, key);
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

/** Brauzer ICU'sida bor til kodi; bo'lmasa `uz`.
 *
 *  Ba'zi kodlar ICU jadvalida YO'Q: `kaa`, `ky`, `tg` — o'lchandi,
 *  ularning uchalasi ham jimgina `en-US` ga tushib, sanani
 *  `9/20/2026, 7:30:00 PM` ko'rinishida beradi. Ya'ni qoraqalpoq
 *  foydalanuvchisi o'zbekchadan ham, ruschadan ham boshqa formatni
 *  ko'rardi. `supportedLocalesOf` ga tayanmaymiz: u ba'zi muhitda
 *  qismiy ma'lumotli tilni ham «bor» deb qaytaradi. Buning o'rniga
 *  natijaning o'zini tekshiramiz — ICU topa olmasa standart tilga
 *  tushadi va bu nomdan ko'rinib turadi.
 */
export function intlLocale(locale: Locale): string {
  try {
    const resolved = new Intl.DateTimeFormat(locale).resolvedOptions().locale;
    return resolved.toLowerCase().startsWith(locale.slice(0, 2))
      ? locale
      : DEFAULT_LOCALE;
  } catch {
    return DEFAULT_LOCALE;
  }
}

/** Sana-vaqtni tilga mos ko'rinishda. Qarang: `intlLocale`. */
export function dateTime(
  value: string | number | Date,
  locale: Locale,
): string {
  return new Date(value).toLocaleString(intlLocale(locale));
}

/** Faqat sana (vaqtsiz) — qarang: `intlLocale`. */
export function date(value: string | number | Date, locale: Locale): string {
  return new Date(value).toLocaleDateString(intlLocale(locale));
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
 *
 * ⚠️ Ko'rinmas qaytish — aldamchi. `zh` foydalanuvchisi o'zbekcha
 * matnni o'z tilidagi tarjima deb o'ylashi mumkin. Shuning uchun
 * `localNameInfo`/`topicNameInfo` qaytishni OSHKOR qiladi va UI
 * yonida kichik `uz` belgisini qo'yadi (qaror 10).
 */
export function topicName(
  topic: { slug: string; name_uz: string; name_ru: string; name_en: string },
  locale: Locale,
): string {
  return topicNameInfo(topic, locale).text;
}

/** Nom + u qaytish (fallback) natijasimi.
 *
 * `fallback` — matn o'zbekchadan olingan, ya'ni so'ralgan tilda
 * tarjima YO'Q. So'ralgan til o'zi `uz` bo'lsa qaytish hisoblanmaydi:
 * o'shanda bu shunchaki to'g'ri javob.
 */
export type NameInfo = {
  text: string;
  locale: Locale | null;
  /** Matn aslida qaysi tildan olingan. */
  source: Locale;
};

function nameInfo(
  row: { name_uz: string; name_ru: string; name_en: string },
  locale: Locale,
): NameInfo {
  const translated =
    locale === "ru" ? row.name_ru : locale === "en" ? row.name_en : "";
  if (translated) return { text: translated, locale, source: locale };
  // So'ralgan til uchun ustun umuman yo'q (`kk`, `zh`, …) yoki bo'sh.
  return { text: row.name_uz, locale: null, source: DEFAULT_LOCALE };
}

/** `localName` + qaytish belgisi. */
export function localNameInfo(
  row: { name_uz: string; name_ru: string; name_en: string },
  locale: Locale,
): NameInfo {
  return nameInfo(row, locale);
}

/** `topicName` + qaytish belgisi. */
export function topicNameInfo(
  topic: { slug: string; name_uz: string; name_ru: string; name_en: string },
  locale: Locale,
): NameInfo {
  const info = nameInfo(topic, locale);
  if (info.text) return info;
  // Nom umuman bo'sh — slug ham matnday o'qiladi, lekin tarjima emas.
  return { text: topic.slug, locale: null, source: DEFAULT_LOCALE };
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
  // `t()` bilan BIR XIL yo'l: dev'da yetishmagan kod yiqiladi, prod'da
  // server matniga tushadi va jurnalga yoziladi. Ilgari bu yerda alohida
  // `?? fallback ?? t(...)` zanjiri bor edi — ya'ni dev'da jim o'tardi.
  return lookup(locale, `error.${code}`, fallback || t(locale, "error.error"));
}
