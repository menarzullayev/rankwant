/** UI tillari — PRD P0-7. App-side wiring for the shared i18n core.
 *
 * ⚠️ MEXANIZM `packages/shared` ga KO'CHDI (2026-09-24, RW-ARCH-013).
 * Ilgari hamma narsa shu faylda edi: til ro'yxati, lug'at reyestri,
 * `t()`/`fill()`, sana formatlash, kontent nomlari. Muammo shunda edi:
 * bu qoidalar — MAHSULOT qarorlari, brauzer qarorlari emas. Ularni
 * ishlatish uchun React/Next dunyosiga kirish kerak edi.
 *
 * Endi:
 *   - qoidalar  → `@rankwant/shared/i18n` (React, Next, DOM yo'q);
 *   - lug'atlar → shu yerda (`./locales/*`), chunki ular — MA'LUMOT.
 *
 * Bu fayl ikkalasini ulaydi va `@/i18n/messages` API'sini O'ZGARISHSIZ
 * saqlaydi — ya'ni 200+ chaqiruv joyi tegmagan.
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
 * The server registers every language (`messages.server.ts`). The browser
 * gets only the active one, as a separate cached file
 * (`app/i18n/[file]/route.ts`), not inside the page: it used to be 72 kB of
 * every page's HTML and a third of the render CPU (2026-09-18 profile).
 *
 * Masala MATNLARI tarjima qilinmaydi — muallif tilida qoladi
 * (Codeforces modeli).
 */

import {
  DEFAULT_LOCALE,
  LOCALES,
  LOCALE_NAMES,
  registerMessages as registerInShared,
  type Dictionary,
  type Locale,
} from "@rankwant/shared/i18n";

import type { MessageKey } from "./locales/uz";

export type { MessageKey };

//: Ilova jamoasi uchun qayta eksport — chaqiruv joylari
//: `@/i18n/messages` dan import qilishda davom etadi.
export { DEFAULT_LOCALE, LOCALES, LOCALE_NAMES };
export type { Locale };

/** Lug'atni shared reyestrga yozadi — lug'at APP tomonida qoladi.
 *
 *  Nom `registerMessages` bo'lib qoldi: `messages.server.ts` va to'rtta
 *  test shuni chaqiradi. Shared paketdagi funksiya import paytida
 *  nomlanadi, ya'ni bu yerda TO'QNASHUV yo'q. */
export function registerMessages(
  locale: Locale,
  dict: Record<MessageKey, string>,
): void {
  //: `Record<MessageKey, string>` — to'liq yozuv; shared esa kengroq
  //: (`Record<string, string>`) kutadi. Toraytirish xavfsiz, kengaytirish
  //: emas — shuning uchun bu yo'nalishda `as unknown` kerak emas, faqat
  //: `Dictionary` interfeysi yetarli.
  registerInShared(locale, dict as Dictionary);
}

export {
  CONTENT_NAME_LOCALES,
  date,
  dateTime,
  errorText,
  evictOtherLocales,
  fill,
  hasContentNames,
  hasMessages,
  intlLocale,
  isLocale,
  localName,
  localNameInfo,
  type NameInfo,
  type Named,
  registrySize,
  resetRegistry,
  t,
  time,
  topicName,
  topicNameInfo,
  translate,
} from "@rankwant/shared/i18n";
