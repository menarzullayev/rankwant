/** O'zbekiston viloyatlari — `profiles/catalog.py` dagi `UZ_REGIONS` bilan
 *  bir xil tartib va kod. Viloyat bo'yicha reyting shu kodlarga tayanadi,
 *  shuning uchun O'zbekistonda viloyat erkin matn emas, ro'yxatdan. */

import type { Locale } from "@/i18n/messages";

const REGIONS: [code: string, uz: string, ru: string, en: string][] = [
  ["toshkent-shahri", "Toshkent shahri", "г. Ташкент", "Tashkent City"],
  ["toshkent", "Toshkent viloyati", "Ташкентская область", "Tashkent Region"],
  ["andijon", "Andijon viloyati", "Андижанская область", "Andijan Region"],
  ["fargona", "Farg'ona viloyati", "Ферганская область", "Fergana Region"],
  ["namangan", "Namangan viloyati", "Наманганская область", "Namangan Region"],
  ["sirdaryo", "Sirdaryo viloyati", "Сырдарьинская область", "Syrdarya Region"],
  ["jizzax", "Jizzax viloyati", "Джизакская область", "Jizzakh Region"],
  ["samarqand", "Samarqand viloyati", "Самаркандская область", "Samarkand Region"],
  ["qashqadaryo", "Qashqadaryo viloyati", "Кашкадарьинская область", "Kashkadarya Region"],
  ["surxondaryo", "Surxondaryo viloyati", "Сурхандарьинская область", "Surkhandarya Region"],
  ["buxoro", "Buxoro viloyati", "Бухарская область", "Bukhara Region"],
  ["navoiy", "Navoiy viloyati", "Навоийская область", "Navoi Region"],
  ["xorazm", "Xorazm viloyati", "Хорезмская область", "Khorezm Region"],
  [
    "qoraqalpogiston",
    "Qoraqalpog'iston Respublikasi",
    "Республика Каракалпакстан",
    "Republic of Karakalpakstan",
  ],
];

/** Kirill yozuvli tillar ruscha nomni, lotin yozuvlilar o'zbekchasini oladi. */
const CYRILLIC: Locale[] = ["ru", "kk", "ky", "tg"];
const LATIN_UZ: Locale[] = ["uz", "kaa", "tr"];

export function regionName(code: string, locale: Locale): string {
  const row = REGIONS.find((r) => r[0] === code);
  if (!row) return code;
  return CYRILLIC.includes(locale)
    ? row[2]
    : LATIN_UZ.includes(locale)
      ? row[1]
      : row[3];
}

export const REGION_CODES = REGIONS.map((r) => r[0]);
