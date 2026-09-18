import { cookies, headers } from "next/headers";

import { LOCALE_COOKIE, LOCALE_HEADER } from "./locale-params";
import type { Locale } from "./messages";
import { resolveLocale } from "./resolve";

// Nomlar `i18n/locale-params.ts` da (proxy ham shuni import qiladi) —
// bu yerdan qayta eksport qilinadi, ya'ni chaqiruvchilar uchun manzil
// o'zgarmaydi.
export { LOCALE_COOKIE, LOCALE_HEADER, LOCALE_PARAM } from "./locale-params";

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

/** Joriy til VA u avtomatik aniqlanganmi.
 *
 *  `locale` — ko'rsatiladigan til; `auto` — odam «Avtomatik» ni
 *  tanlaganmi. Ikkalasi kerak: tanlagich qaysi variant belgilanganini
 *  shu bilan biladi, holbuki `locale` doim aniq til bo'ladi.
 *
 *  Ustunlik tartibi `./resolve` da (sof funksiya, unit-testda
 *  tekshiriladi). Bu yerda faqat uchta MANBA o'qiladi:
 *
 *    `?lang=` → proxy uni so'rov sarlavhasiga ko'chirgan (LOCALE_HEADER)
 *    cookie   → odam tanlagan (yoki proxy havoladan yozgan) qiymat
 *    sarlavha → brauzer taklifi, birinchi taassurot uchun
 *
 *  ⚠️ `Vary: Accept-Language` shu funksiya uchun SHART: javob sarlavhaga
 *  bog'liq, ya'ni kesh uni alohida saqlashi kerak. Bugun `no-store`
 *  turganda zarari yo'q, lekin keshlash yoqilsa bir zumda kesh-zaharlash
 *  xatosiga aylanadi — bir xil URL rus foydalanuvchisiga inglizcha
 *  beriladi (o'lchandi: bitta URL, to'rt til). Endi URL'da `?lang=` bor,
 *  ya'ni savol yana bir pog'ona o'tkirroq.
 */
export async function getLocaleState(): Promise<{ locale: Locale; auto: boolean }> {
  const requestHeaders = await headers();
  return resolveLocale(
    requestHeaders.get(LOCALE_HEADER),
    (await cookies()).get(LOCALE_COOKIE)?.value ?? null,
    requestHeaders.get("accept-language"),
  );
}

/** Server komponentlari uchun joriy til — faqat `locale` (qarang:
 *  `getLocaleState`, u `auto` ni ham qaytaradi). */
export async function getLocale(): Promise<Locale> {
  return (await getLocaleState()).locale;
}
