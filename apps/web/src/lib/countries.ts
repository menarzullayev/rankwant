/** Mamlakatlar — ISO 3166-1 alpha-2.
 *
 * Nom ikki manbadan: `country-names.ts` jadvali (uz + ru) va brauzerning
 * `Intl.DisplayNames` i. Ikkalasi kerak — pastga qarang.
 */

import type { Locale } from "@/i18n/messages";
import { COUNTRY_NAMES } from "./country-names";

const CODES =
  "AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW".split(
    " ",
  );

/** Ro'yxat boshida — foydalanuvchilarning asosiy qismi shu yerdan. */
const PINNED = ["UZ", "KZ", "KG", "TJ", "TM", "RU", "TR"];

/** Jadval qaysi tillarga xizmat qiladi.
 *
 * ⚠️ `Intl.DisplayNames` faqat uz/ru da ishlamaydi degan taxmin NOTO'G'RI
 * edi. Chrome'da o'lchandi: ICU to'rt tilda ham hudud ma'lumotini bermaydi
 * va inglizchaga tushadi — `kaa`, `kk`, `ky`, `tg`. `kaa` da hatto
 * `kaa-Latn` / `kaa-Cyrl` teglari ham bo'sh.
 *
 * Node bilan o'lchash ALDAMCHI: Node `kk`/`ky`/`tg` uchun ruscha qaytaradi,
 * brauzer esa yo'q. Ya'ni bu ro'yxat brauzerdagi o'lchovga tayanishi shart.
 *
 * Kirill yozuvli tillar ruscha nomni oladi (qoraqalpoqchadan tashqari
 * hammasi shu guruhda) — bu `lib/regions.ts` dagi bilan AYNAN bir xil
 * qoida, shuning uchun viloyat va mamlakat nomlari bir uslubda chiqadi.
 */
const CYRILLIC: Locale[] = ["ru", "kk", "ky", "tg"];
//: `tr` ataylab YO'Q: turkchada ICU hudud nomlarini o'zi beradi
//: ("Almanya", "Amerika Birleşik Devletleri") va jadval uni buzardi —
//: o'lchandi: `tr` ni qo'shganda "Almanya" o'rniga "Germaniya" chiqdi.
const LATIN_UZ: Locale[] = ["uz", "kaa"];

/** Mamlakat nomi: jadval → ICU → kod.
 *
 * Jadval BIRINCHI turadi, chunki yuqoridagi tillarda Chrome'ning
 * `Intl.DisplayNames` i hudud nomini bermaydi (inglizchaga tushadi) —
 * natijada o'sha tillardagi UI da "Germany" chiqardi va qidiruvda
 * mahalliy nom topilmasdi.
 *
 * `regions.ts` dagi guruhlar bilan AYNAN bir xil emas va bo'lishi ham
 * shart emas: viloyat nomlari uchun turkcha ma'lumot yo'q, mamlakat
 * nomlari uchun bor.
 */
export function countryName(code: string, locale: Locale): string {
  const iso = code.toUpperCase();
  const row = COUNTRY_NAMES[iso];
  if (row) {
    if (CYRILLIC.includes(locale)) return row[1];
    if (LATIN_UZ.includes(locale)) return row[0];
  }
  // `en`, `zh`, `es` — ICU shu uchtasini haqiqatan qoplaydi.
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
