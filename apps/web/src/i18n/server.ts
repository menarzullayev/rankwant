import { cookies } from "next/headers";

import { DEFAULT_LOCALE, isLocale, type Locale } from "./messages";

/** Til tanlovi saqlanadigan cookie. */
export const LOCALE_COOKIE = "rw_locale";

/** Server komponentlari uchun joriy til.
 *
 * Cookie, `Accept-Language` emas: brauzer tili odatda foydalanuvchi
 * TANLAGAN til emas, va sarlavha bo'yicha o'zgaradigan javobni kesh
 * ham ushlay olmaydi.
 */
export async function getLocale(): Promise<Locale> {
  const value = (await cookies()).get(LOCALE_COOKIE)?.value;
  return isLocale(value) ? value : DEFAULT_LOCALE;
}
