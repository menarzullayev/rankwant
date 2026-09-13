import "server-only";

import { registerMessages, type Locale, type MessageKey } from "./messages";
import { en } from "./locales/en";
import { es } from "./locales/es";
import { kaa } from "./locales/kaa";
import { kk } from "./locales/kk";
import { ky } from "./locales/ky";
import { ru } from "./locales/ru";
import { tg } from "./locales/tg";
import { tr } from "./locales/tr";
import { uz } from "./locales/uz";
import { zh } from "./locales/zh";

/** Server tomonidagi lug'atlar — o'ntasi ham.
 *
 *  Nega hammasi bu yerda, `messages.ts` da emas: Node'da hajm muhim emas,
 *  mijozga esa bu to'plam UMUMAN bormaydi — fayl `server-only` bilan
 *  belgilangan, uni faqat `layout.tsx` import qiladi. Klientga faqat aktiv
 *  til uzatiladi (inline skript, `layout.tsx` ga qarang).
 *
 *  Ro'yxatga olish MODUL ishga tushishida bo'ladi, ya'ni `t()` ni
 *  chaqiruvchi har qanday server komponentidan OLDIN bajariladi.
 *
 *  ⚠️ `evict` ATAYLAB berilmaydi: bu tsikl o'nta tilni ham ro'yxatga
 *  oladi va serverda ularning barchasi kerak. Bir marta bu joyda
 *  chegaralash (`registry.clear()`) bor edi va tsikl faqat oxirgi
 *  tilni qoldirardi — natijada SSR'da o'nlab xom kalit chiqqan
 *  (`home.start`, `nav.contests`, …, o'lchandi).
 */
const ALL: Record<Locale, Record<MessageKey, string>> = {
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

for (const [locale, dict] of Object.entries(ALL)) {
  registerMessages(locale as Locale, dict);
}

/** Aktiv tilning lug'ati — `layout.tsx` shuni mijozga uzatadi. */
export function messagesFor(locale: Locale): Record<MessageKey, string> {
  return ALL[locale] ?? ALL.uz;
}
