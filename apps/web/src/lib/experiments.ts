/** Eksperiment guruhi — `lib/flags.ts` ga ko'chirildi.
 *
 *  ⚠️ Bu fayl **moslik qobig'i** (`shim`): eski import yo'llari
 *  (`./experiments`) ishlashda davom etsin, lekin mantiq endi bitta
 *  joyda — `lib/flags.ts` da yashaydi.
 *
 *  Nega birlashtirildi: eksperiment — bu ham **bayroq**, faqat
 *  qiymati cookie'dagi tasodifiy guruhdan keladi. Ikki fayl bo'lsa
 *  ikkita cookie o'qish, ikkita parse qilish va ikkita "o'chirish
 *  yo'li" bo'lardi. Endi bitta reyestr: `FLAGS` + `EXPERIMENT_FLAGS`.
 *
 *  Yangi kod to'g'ridan-to'g'ri `@/lib/flags` dan import qilsin.
 */

import { EXP_COOKIE as COOKIE, parseVariant } from "./flags";

export { EXP_COOKIE, isOn } from "./flags";

/** Eksperiment nomi — `lib/flags.ts` dagi `EXPERIMENT_FLAGS` bilan
 *  bog'langan (`geoEarlyRegion` -> `geo`). Bu yerda `analytics.ts` uchun
 *  saqlanadi: hodisaga guruh qo'shilishi kerak. */
export const GEO_EXPERIMENT = "geo";

export type Variant = "a" | "b";

/** Cookie matnidan guruhni ajratadi — sof funksiya.
 *
 *  Qiymat yo'q yoki buzuq bo'lsa `a` qaytadi: standart xatti-harakat
 *  o'zgarmasligi kerak, ya'ni noma'lum holatda eksperiment qo'llanmaydi. */
export function parseVariants(raw: string | undefined, name: string): Variant {
  return parseVariant(raw, name);
}

/** Mijozda cookie'dan guruhni o'qiydi.
 *
 *  ⚠️ Server komponentida ishlatilmaydi: u yerda `document` yo'q, ya'ni
 *  funksiya har doim `a` qaytarardi va server `a`, mijoz `b` chizib
 *  hidratsiya mos kelmasligi mumkin edi. Server tomon uchun
 *  `isOnServer` ni `cookies()` bilan birga ishlatish kerak
 *  (`lib/flags.ts`). */
export function variant(name: string): Variant {
  if (typeof document === "undefined") return "a";
  const raw = document.cookie.match(
    new RegExp(`(?:^|;\s*)${COOKIE}=([^;]+)`),
  )?.[1];
  return parseVariant(raw ? decodeURIComponent(raw) : undefined, name);
}
