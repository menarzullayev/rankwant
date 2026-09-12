/** Mamlakatlar — ISO 3166-1 alpha-2. Nomi brauzerning o'zidan
 *  (`Intl.DisplayNames`) olinadi: 250 ta nomni o'n tilda qo'lda saqlash
 *  shart emas va u doim to'g'ri yoziladi. */

import type { Locale } from "@/i18n/messages";
import { COUNTRY_NAMES } from "./country-names";

const CODES =
  "AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW".split(
    " ",
  );

/** Ro'yxat boshida — foydalanuvchilarning asosiy qismi shu yerdan. */
const PINNED = ["UZ", "KZ", "KG", "TJ", "TM", "RU", "TR"];

/** Mamlakat nomi: jadval → ICU → kod.
 *
 * Jadval BIRINCHI turadi, chunki bu Chrome'da `Intl.DisplayNames`
 * o'zbekcha nomlarni bermaydi (inglizchaga tushadi) — natijada o'zbekcha
 * UI da "Uzbekistan" chiqardi va qidiruvda "qoz" topilmasdi.
 * Boshqa tillar uchun ICU ishlaydi, ya'ni jadval faqat uz/ru ni qoplaydi.
 */
export function countryName(code: string, locale: Locale): string {
  const iso = code.toUpperCase();
  const row = COUNTRY_NAMES[iso];
  if (row && (locale === "uz" || locale === "ru")) {
    return locale === "ru" ? row[1] : row[0];
  }
  try {
    return new Intl.DisplayNames([locale, "en"], { type: "region" }).of(iso) ?? iso;
  } catch {
    return iso;
  }
}

export function countryOptions(locale: Locale): { code: string; name: string }[] {
  // `countryName` orqali — jadval (uz/ru) va ICU (qolgan tillar) bir
  // joyda hal qilinadi, ya'ni ro'yxat va bitta nom bir xil chiqadi.
  const named = (code: string) => ({ code, name: countryName(code, locale) });
  const rest = CODES.filter((c) => !PINNED.includes(c))
    .map(named)
    .sort((a, b) => a.name.localeCompare(b.name, locale));
  return [...PINNED.map(named), ...rest];
}
