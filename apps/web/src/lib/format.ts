import type { Locale } from "@/i18n/messages";

/** Intl qo'llamaydigan til (qoraqalpoq) o'zbekchaga tushadi, ingliz
 *  tiliga emas. Robocontest'da sana va nisbiy vaqt interfeys tilidan
 *  qat'i nazar kirillda chiqardi — shu yerda bitta qoida bilan yopiladi. */
export const dateLocales = (locale: Locale): string[] => [locale, "uz"];

/** API'dagi `TIME_ZONE`: faollik xaritasi va streak kunlari shu zonada
 *  sanaladi, sanalar ham shu zonada ko'rsatiladi (web server UTC'da). */
export const SITE_TZ = "Asia/Tashkent";

export function formatDate(
  value: string | Date,
  locale: Locale,
  options: Intl.DateTimeFormatOptions = { dateStyle: "medium" },
): string {
  return new Intl.DateTimeFormat(dateLocales(locale), { timeZone: SITE_TZ, ...options }).format(
    new Date(value),
  );
}

/** Client komponent uchun oy va hafta kuni nomlari. SERVERDA hisoblanib
 *  prop bo'lib beriladi: brauzer ICU'sida uz, kk, ky, tg sana ma'lumoti
 *  yo'q — u yerda `Intl` «2026 M09 9», «Wed» qaytaradi va server HTML'i
 *  bilan mos kelmay hydration xatosi chiqaradi. */
export type DateKit = {
  /** `{y}`, `{M}`, `{d}` (qozoq, tojikda ikki xonali `{dd}`) o'rinli qolip:
   *  «{d}-{M}, {y}». */
  pattern: string;
  /** Sana ichidagi qisqa oy nomi (ruschada qaratqich: «сент.»). */
  monthsOf: string[];
  /** Yakka qisqa oy nomi — o'q yorliqlari uchun. */
  months: string[];
  /** Dushanbadan boshlab qisqa hafta kunlari. */
  weekdays: string[];
};

const PART: Partial<Record<Intl.DateTimeFormatPartTypes, string>> = { year: "{y}", month: "{M}" };

/** V8 `format()` natijasida U+202F ni oddiy probelga almashtiradi,
 *  `formatToParts()` esa yo'q — `formatDate` bilan bir xil chiqsin. */
const plain = (value: string) => value.replace(/\u202f/g, " ");

export function dateKit(locale: Locale): DateKit {
  const locales = dateLocales(locale);
  const medium = new Intl.DateTimeFormat(locales, { dateStyle: "medium", timeZone: "UTC" });
  const month = new Intl.DateTimeFormat(locales, { month: "short", timeZone: "UTC" });
  const weekday = new Intl.DateTimeFormat(locales, { weekday: "short", timeZone: "UTC" });
  const ninth = (m: number) => new Date(Date.UTC(2026, m, 9));
  return {
    pattern: medium
      .formatToParts(ninth(8))
      .map((part) =>
        part.type === "day"
          ? part.value.length === 2
            ? "{dd}"
            : "{d}"
          : (PART[part.type] ?? plain(part.value)),
      )
      .join(""),
    monthsOf: Array.from(
      { length: 12 },
      (_, m) => medium.formatToParts(ninth(m)).find((part) => part.type === "month")?.value ?? "",
    ),
    months: Array.from({ length: 12 }, (_, m) => plain(month.format(ninth(m)))),
    // 2024-01-01 — dushanba.
    weekdays: Array.from({ length: 7 }, (_, i) =>
      plain(weekday.format(new Date(Date.UTC(2024, 0, 1 + i)))),
    ),
  };
}

/** en-US va vaqt zonalari har brauzerda bor — natija hamma joyda bir xil. */
const DAY_PARTS = new Intl.DateTimeFormat("en-US", {
  timeZone: SITE_TZ,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

/** Vaqt belgisining sayt zonasidagi kuni: «2026-09-09». */
export function isoDay(value: string | Date): string {
  const parts = Object.fromEntries(
    DAY_PARTS.formatToParts(new Date(value)).map((part) => [part.type, part.value]),
  );
  return `${parts.year}-${parts.month}-${parts.day}`;
}

/** «2026-09-09» yoki vaqt belgisi → `kit` qolipidagi sana. */
export function formatDay(kit: DateKit, value: string): string {
  const [y, m, d] = (/^\d{4}-\d{2}-\d{2}$/.test(value) ? value : isoDay(value))
    .split("-")
    .map(Number);
  return kit.pattern
    .replace("{y}", String(y))
    .replace("{M}", kit.monthsOf[m - 1])
    .replace("{dd}", String(d).padStart(2, "0"))
    .replace("{d}", String(d));
}

const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 86400],
  ["month", 30 * 86400],
  ["day", 86400],
  ["hour", 3600],
  ["minute", 60],
];

/** «5 daqiqa oldin» — tanlangan tilda. FAQAT serverda: brauzer ICU'sida
 *  uz, kk, ky, tg ma'lumoti yo'q (`DateKit` izohiga qarang). */
export function formatRelative(value: string | Date, locale: Locale, now = Date.now()): string {
  const seconds = Math.round((new Date(value).getTime() - now) / 1000);
  const rtf = new Intl.RelativeTimeFormat(dateLocales(locale), { numeric: "auto" });
  for (const [unit, size] of UNITS) {
    if (Math.abs(seconds) >= size) return rtf.format(Math.round(seconds / size), unit);
  }
  return rtf.format(0, "minute");
}

/** Ulush foizda, tanlangan til ajratgichi bilan: 0,05 → «<0,1», 12,3 → «12». */
export function formatShare(value: number, locale: Locale): string {
  const number = (n: number, digits: number) =>
    new Intl.NumberFormat(dateLocales(locale), { maximumFractionDigits: digits }).format(n);
  if (value > 0 && value < 0.1) return `<${number(0.1, 1)}`;
  return number(value, value < 10 ? 1 : 0);
}

/** 135 → «2:15». */
export function formatDuration(minutes: number): string {
  return `${Math.floor(minutes / 60)}:${String(minutes % 60).padStart(2, "0")}`;
}

/** Masala raqami — `#0431` ko'rinishida. */
export const padCode = (code: number | null) =>
  code === null ? "—" : String(code).padStart(4, "0");
