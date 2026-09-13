import { cookies, headers } from "next/headers";

import { DEFAULT_LOCALE, isLocale, type Locale } from "./messages";

/** Til tanlovi saqlanadigan cookie. */
export const LOCALE_COOKIE = "rw_locale";

/** «Avtomatik» markeri — odam tanlagan, til esa sarlavhadan aniqlanadi.
 *
 *  Cookie'ni BUTUNLAY o'chirib bo'lmaydi: `PrefsSync` cookie yo'qligini
 *  «hali tanlanmagan» deb tushunadi va hisobdagi til bilan qayta
 *  to'ldiradi, ya'ni «Avtomatik» darhol bekor bo'lardi (o'lchandi —
 *  kod oqimidan). Shu sababli ikki holat ajratiladi:
 *
 *    cookie yo'q      → hali tanlanmagan, hisob urug'i qo'llanadi
 *    `rw_locale=auto` → ataylab avtomatik, urug' qo'llanmaydi
 */
export const LOCALE_AUTO = "auto";

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
 *
 * `rw_locale=auto` — odam «Avtomatik» ni ATAYLAB tanlagan holat: cookie
 * bor, lekin u til emas, shuning uchun sarlavhadan aniqlashga o'tamiz.
 *
 * ⚠️ `Vary: Accept-Language` shu funksiya uchun SHART: javob sarlavhaga
 * bog'liq, ya'ni kesh uni alohida saqlashi kerak. Bugun `no-store`
 * turganda zarari yo'q, lekin keshlash yoqilsa bir zumda kesh-zaharlash
 * xatosiga aylanadi — bir xil URL rus foydalanuvchisiga inglizcha
 * beriladi (o'lchandi: bitta URL, to'rt til).
 */
/** Joriy til VA u avtomatik aniqlanganmi.
 *
 *  `locale` — ko'rsatiladigan til; `auto` — odam «Avtomatik» ni
 *  tanlaganmi. Ikkalasi kerak: tanlagich qaysi variant belgilanganini
 *  shu bilan biladi, holbuki `locale` doim aniq til bo'ladi.
 */
export async function getLocaleState(): Promise<{ locale: Locale; auto: boolean }> {
  const chosen = (await cookies()).get(LOCALE_COOKIE)?.value;
  if (isLocale(chosen)) return { locale: chosen, auto: false };

  const detected = fromAcceptLanguage((await headers()).get("accept-language"));
  return {
    locale: detected ?? DEFAULT_LOCALE,
    // `auto` markeri ham, umuman cookie yo'qligi ham avtomatik holat.
    auto: true,
  };
}

/** Server komponentlari uchun joriy til — faqat `locale` (qarang:
 *  `getLocaleState`, u `auto` ni ham qaytaradi). */
export async function getLocale(): Promise<Locale> {
  return (await getLocaleState()).locale;
}
