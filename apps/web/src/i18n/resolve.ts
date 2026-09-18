import { DEFAULT_LOCALE, isLocale, type Locale } from "./messages";

/** `Accept-Language` sarlavhasidan mos tilni tanlaydi.
 *
 * Faqat COOKIE va havola bo'lmaganda ishlatiladi: cookie — odamning O'ZI
 * tanlagan tili, ya'ni u har doim ustun. Sarlavha esa birinchi taassurot
 * uchun: chet ellik foydalanuvchi qo'lda almashtirmasdan o'z tilida
 * boshlaydi (qaror 14). Aks holda u o'zbekcha ko'rib, ro'yxatdan o'tmasdan
 * ketishi mumkin edi.
 *
 * Sifat koeffitsienti (`q=`) hisobga olinadi — brauzerlar tartibni shu
 * bilan bildiradi, satr tartibi bilan emas. `uz-Latn-UZ` kabi variant
 * asosiy tilga (`uz`) tushadi, `*` esa tashlab ketiladi.
 */
export function fromAcceptLanguage(header: string | null): Locale | null {
  if (!header) return null;

  const ranked = header
    .split(",")
    .map((part) => {
      const [tag = "", ...params] = part.trim().split(";");
      const q = params.find((p) => p.trim().startsWith("q="));
      const quality = q ? Number(q.split("=")[1]) : 1;
      return { tag: tag.trim().toLowerCase(), quality };
    })
    .filter((entry) => entry.tag && entry.tag !== "*" && entry.quality > 0)
    .sort((a, b) => b.quality - a.quality);

  for (const { tag } of ranked) {
    const base = tag.split("-")[0];
    if (isLocale(base)) return base;
  }
  return null;
}

/** Joriy til — ustunlik tartibi bo'yicha. Sof funksiya: kirish uchtalik,
 *  chiqish aniq javob. Shu sababli unit-testda tekshiriladi (tarmoq,
 *  cookie, `next/headers` kerak emas).
 *
 * TARTIB: `?lang=` → cookie → `Accept-Language` → standart.
 *
 * 1. `?lang=` — HAVOLA ustun (qaror S5, 2026-09-19). Sabab: ulashilgan
 *    havola o'z tilini o'zi bilan olib kelishi kerak; olgan odamning
 *    qurilmasida boshqa til tanlangan bo'lishi mumkin. Havola aniq
 *    so'rov, ya'ni u qurilma tanlovidan kuchliroq.
 * 2. cookie — odamning o'zi tanlagan tili (yoki proxy yozgan qiymat).
 * 3. `Accept-Language` — brauzer taklif qilgan, ya'ni birinchi taassurot.
 * 4. standart (`uz`).
 *
 * `rw_locale=auto` — odam «Avtomatik» ni ATAYLAB tanlagan holat: cookie
 * bor, lekin u til EMAS, shuning uchun sarlavhadan aniqlashga o'tamiz va
 * `auto: true` qaytaramiz.
 *
 * Notanish qiymat (`?lang=xx`, buzilgan cookie) JIM tashlab ketiladi va
 * keyingi pog'onaga o'tiladi — sahifa bo'sh qolmaydi.
 */
export function resolveLocale(
  param: string | null,
  cookie: string | null,
  acceptLanguage: string | null,
): { locale: Locale; auto: boolean } {
  if (param !== null && isLocale(param)) return { locale: param, auto: false };
  if (cookie !== null && isLocale(cookie)) return { locale: cookie, auto: false };
  return {
    locale: fromAcceptLanguage(acceptLanguage) ?? DEFAULT_LOCALE,
    // `auto` markeri ham, umuman tanlov yo'qligi ham avtomatik holat.
    auto: true,
  };
}
