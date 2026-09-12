import { cookies, headers } from "next/headers";

import { DEFAULT_LOCALE, isLocale, type Locale } from "./messages";

/** Til tanlovi saqlanadigan cookie. */
export const LOCALE_COOKIE = "rw_locale";

/** `Accept-Language` sarlavhasidan mos tilni tanlaydi.
 *
 * Faqat COOKIE bo'lmaganda ishlatiladi: cookie — odamning O'ZI tanlagan
 * tili, ya'ni u har doim ustun. Sarlavha esa birinchi taassurot uchun:
 * chet ellik foydalanuvchi qo'lda almashtirmasdan o'z tilida boshlaydi
 * (qaror 14). Aks holda u o'zbekcha ko'rib, ro'yxatdan o'tmasdan
 * ketishi mumkin edi.
 *
 * Sifat koeffitsienti (`q=`) hisobga olinadi — brauzerlar tartibni shu
 * bilan bildiradi, satr tartibi bilan emas. `uz-Latn-UZ` kabi variant
 * asosiy tilga (`uz`) tushadi, `*` esa tashlab ketiladi.
 */
function fromAcceptLanguage(header: string | null): Locale | null {
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

/** Server komponentlari uchun joriy til.
 *
 * Ustunlik tartibi: cookie (odam tanlagan) → `Accept-Language` (brauzer
 * taklif qilgan) → standart. Ya'ni avtomatik aniqlash odamning tanlovini
 * HECH QACHON bekor qilmaydi — u faqat tanlov bo'lmaganda ishlaydi.
 */
export async function getLocale(): Promise<Locale> {
  const chosen = (await cookies()).get(LOCALE_COOKIE)?.value;
  if (isLocale(chosen)) return chosen;

  return (
    fromAcceptLanguage((await headers()).get("accept-language")) ??
    DEFAULT_LOCALE
  );
}
