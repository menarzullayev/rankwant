import type { Locale } from "@/i18n/messages";

/** Intl qo'llamaydigan til (qoraqalpoq) o'zbekchaga tushadi, ingliz
 *  tiliga emas. Robocontest'da sana va nisbiy vaqt interfeys tilidan
 *  qat'i nazar kirillda chiqardi — shu yerda bitta qoida bilan yopiladi. */
export const dateLocales = (locale: Locale): string[] => [locale, "uz"];

export function formatDate(
  value: string | Date,
  locale: Locale,
  options: Intl.DateTimeFormatOptions = { dateStyle: "medium" },
): string {
  return new Date(value).toLocaleDateString(dateLocales(locale), options);
}

/** 135 → «2:15». */
export function formatDuration(minutes: number): string {
  return `${Math.floor(minutes / 60)}:${String(minutes % 60).padStart(2, "0")}`;
}

/** Masala raqami — `#0431` ko'rinishida. */
export const padCode = (code: number | null) =>
  code === null ? "—" : String(code).padStart(4, "0");
