import "server-only";

import { createHash } from "node:crypto";

import { toNewAlphabet } from "@rankwant/shared/alphabet";
import { registerVariant, setVariantResolver } from "@rankwant/shared/i18n";

import { ALPHABET_LOCALE, type Alphabet } from "./alphabet";
import { requestAlphabet } from "./alphabet-store.server";
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

/** Uzbek as the source is written (the old alphabet) and as it is shown by
 *  default — the new alphabet of O'RQ-1184 (ADR-0059). Converted once, when
 *  the module loads, so translators keep writing `uz.ts` as before. */
const UZ_OLD: Record<MessageKey, string> = uz;
const UZ_NEW = Object.fromEntries(
  Object.entries(uz).map(([key, text]) => [key, toNewAlphabet(text)]),
) as Record<MessageKey, string>;

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
  uz: UZ_NEW,
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

// The old alphabet is a variant of `uz`; the request picks it through its
// `rw_alphabet` cookie, which `instrumentation.ts` puts into the request's
// context. Every request in the process shares this registry.
registerVariant(ALPHABET_LOCALE, "old", UZ_OLD);
setVariantResolver((locale) =>
  locale === ALPHABET_LOCALE && requestAlphabet() === "old" ? "old" : null,
);

const isOld = (locale: Locale, alphabet: Alphabet) =>
  locale === ALPHABET_LOCALE && alphabet === "old";

const hash = (dict: Record<MessageKey, string>) =>
  createHash("sha256").update(JSON.stringify(dict)).digest("hex").slice(0, 12);

/** Short content hash per dictionary. The file is cached for a year, so a
 *  changed dictionary must get a new address. */
const VERSION = Object.fromEntries(
  Object.entries(ALL).map(([locale, dict]) => [locale, hash(dict)]),
) as Record<Locale, string>;
const OLD_VERSION = hash(UZ_OLD);

/** The dictionary file's name: `uz.js`, or `uz-old.js` for the old alphabet. */
export function dictionaryFile(locale: Locale, alphabet: Alphabet = "new"): string {
  return isOld(locale, alphabet) ? `${locale}-old.js` : `${locale}.js`;
}

/** Address of the dictionary file for `locale`. */
export function dictionaryUrl(locale: Locale, alphabet: Alphabet = "new"): string {
  const version = isOld(locale, alphabet) ? OLD_VERSION : VERSION[locale];
  return `/i18n/${dictionaryFile(locale, alphabet)}?v=${version}`;
}

/** The dictionary file: it registers `locale` in the browser's registry,
 *  and creates that registry when the app code has not loaded yet (see
 *  `registry` in `messages.ts`). Both alphabets register under the locale
 *  itself: a page shows one. */
export function dictionaryScript(locale: Locale, alphabet: Alphabet = "new"): string {
  const dict = isOld(locale, alphabet) ? UZ_OLD : ALL[locale];
  return `(self.__rwMessages=self.__rwMessages||new Map()).set(${JSON.stringify(locale)},${JSON.stringify(dict)});\n`;
}
