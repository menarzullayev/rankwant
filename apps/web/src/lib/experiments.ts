/** Eksperiment guruhi — barqaror va sahifa yuklanishlari orasida saqlanadi.
 *
 * Guruh SERVERDA (`proxy.ts`) belgilanadi va cookie'ga yoziladi. Mijozda
 * tasodifiy tanlansa, sahifa har yuklanishida guruh o'zgarib ketardi va
 * bir odam ikki guruhda ham hisoblanardi — o'lchov ma'nosini yo'qotardi.
 *
 * Cookie `HttpOnly` EMAS: mijoz uni o'qib formani shunga qarab chizadi.
 * Bu xavfsiz — guruh qiymati maxfiy emas va hech qanday huquq bermaydi.
 */

export const EXP_COOKIE = "rw_exp";

export type Variant = "a" | "b";

/** Viloyat qachon so'raladi (8-qaror).
 *
 * `a` — NAZORAT: viloyat 2-qadamda (hozirgi holat).
 * `b` — VARIANT: viloyat ro'yxatdan o'tishning o'zida.
 *
 * Taqqoslanadigan ko'rsatkich — ro'yxatdan o'tishni tugatgan sessiyalar,
 * ya'ni viloyatni erta so'rash odamni qaytarib yubormayaptimi.
 */
export const GEO_EXPERIMENT = "geo";

/** Cookie qiymatini guruhga aylantiradi — SOF funksiya.
 *
 * Guruh yo'q yoki buzuq bo'lsa `a` qaytadi: standart xatti-harakat
 * o'zgarmasligi kerak, ya'ni noma'lum holatda eksperiment qo'llanmaydi.
 *
 * Format: `geo:b,other:a` — bir nechta tajriba bitta cookie'da.
 */
export function parseVariants(raw: string | undefined, name: string): Variant {
  if (!raw) return "a";
  for (const part of raw.split(",")) {
    const [key, value] = part.split(":");
    if (key === name && (value === "a" || value === "b")) return value;
  }
  return "a";
}

/** Mijozda cookie'dan guruhni o'qiydi.
 *
 * Server komponentida ishlatilmaydi: u yerda `document` yo'q, ya'ni
 * funksiya har doim `a` qaytarardi va server `a`, mijoz `b` chizib
 * hidratsiya mos kelmasligi mumkin edi. Server tomon uchun
 * `parseVariants` ni `cookies()` bilan birga ishlatish kerak.
 */
export function variant(name: string): Variant {
  if (typeof document === "undefined") return "a";
  const raw = document.cookie.match(/(?:^|;\s*)rw_exp=([^;]+)/)?.[1];
  return parseVariants(raw ? decodeURIComponent(raw) : undefined, name);
}
