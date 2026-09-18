import "server-only";

import { createHash } from "node:crypto";

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
 *  belgilangan. The browser receives only the active language, as the file
 *  that `dictionaryScript` produces (served by `app/i18n/[file]/route.ts`).
 *
 *  Ro'yxatga olish MODUL ishga tushishida bo'ladi, ya'ni `t()` ni
 *  chaqiruvchi har qanday server komponentidan OLDIN bajariladi.
 *
 *  Serverda ularning barchasi kerak. Bir marta bu joyda
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

/** Short content hash per dictionary. The file is cached for a year, so a
 *  changed dictionary must get a new address. */
const VERSION = Object.fromEntries(
  Object.entries(ALL).map(([locale, dict]) => [
    locale,
    createHash("sha256").update(JSON.stringify(dict)).digest("hex").slice(0, 12),
  ]),
) as Record<Locale, string>;

/** Address of the dictionary file for `locale`. */
export function dictionaryUrl(locale: Locale): string {
  return `/i18n/${locale}.js?v=${VERSION[locale]}`;
}

/** The dictionary file: it registers `locale` in the browser's registry,
 *  and creates that registry when the app code has not loaded yet (see
 *  `registry` in `messages.ts`). */
export function dictionaryScript(locale: Locale): string {
  return `(self.__rwMessages=self.__rwMessages||new Map()).set(${JSON.stringify(locale)},${JSON.stringify(ALL[locale])});\n`;
}
