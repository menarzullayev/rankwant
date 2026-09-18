/** Til tanlashning uch nomi — YAGONA manba.
 *
 *  Nega alohida fayl: proxy (edge runtime) `next/headers` ni import qila
 *  OLMAYDI, ya'ni `i18n/server.ts` unga ko'rinmaydi. Nomlarni ikki joyda
 *  takrorlash esa drift manbai: bir tomon o'zgarsa ikkinchisi jim qoladi
 *  va til almashinuvi sababsiz ishlamay qo'yadi.
 *
 *  Bu fayl HECH NARSANI import qilmaydi — shuning uchun edge'da ham,
 *  server komponentida ham, vitest'da ham bir xil yuklanadi.
 */

/** Tanlangan til saqlanadigan cookie. */
export const LOCALE_COOKIE = "rw_locale";

/** Havolada tilni uzatuvchi query parametri (`?lang=ru`). */
export const LOCALE_PARAM = "lang";

/** Proxy tilni JORIY render'ga shu sarlavha orqali uzatadi.
 *
 *  `?lang=` ni faqat proxy ko'radi — u har so'rovda butun URL'ni oladi,
 *  sahifa esa yo'q: `searchParams` sahifa ichida qoladi, ya'ni layout uni
 *  ko'rmaydi. Shuning uchun qiymat so'rov sarlavhasiga ko'chiriladi va
 *  `next/headers` orqali o'qiladi. */
export const LOCALE_HEADER = "x-rw-locale";
