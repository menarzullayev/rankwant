import { LOCALE_COOKIE } from "@/i18n/locale-params";

/**
 * Bosh sahifa HTML keshi — 100 000 bir vaqtdagi ochilish qarorlari
 * (2026-09-19): faqat GET `/`, faqat mehmon, origin Cache-Control,
 * s-maxage=30 + stale-while-revalidate.
 *
 * Next.js layout `cookies()` o'qiydi va o'zi `private, no-store` yozadi.
 * Shu modul qarorni aytadi; `proxy.ts` va `instrumentation.ts` uni
 * javobga qo'yadi. Cloudflare esa origin header'ga rioya qiladi.
 */

/** Django standart sessiya cookie — `SESSION_COOKIE_NAME` o'zgarmagan. */
export const SESSION_COOKIE = "sessionid";

/** Markup HTML tuzilishini o'zgartiradi (`prefs.ts` dagi `MARKUP_COOKIE`). */
export const HOME_MARKUP_COOKIE = "rw:markup";

/** Keshlangan mehmon HTML doim shu tilda — `Accept-Language` zaharlamasligi uchun. */
export const HOME_CACHE_LOCALE = "uz";

export const HOME_CACHE_PATH = "/";

/** Proxy → Node instrumentation. Next `Cookie` ni `res.req` da yo'qotishi mumkin. */
export const HOME_CACHE_REQUEST_HEADER = "x-rw-home-cache";
export const HOME_CACHE_MARK_GUEST = "guest";
export const HOME_CACHE_MARK_PRIVATE = "private";

/** Mehmon: CDN 30 s, keyin stale-while-revalidate. */
export const HOME_CACHE_GUEST =
  "public, s-maxage=30, stale-while-revalidate=86400";

/** Kirgan (yoki shaxsiylashtirilgan mehmon): CDN saqlamasin. */
export const HOME_CACHE_PRIVATE = "private, no-store";

/** Next.js App Router hujjat so'rovidan RCS/prefetch ni ajratadi. */
const RSC_HINTS = [
  "rsc",
  "next-router-prefetch",
  "next-router-state-tree",
  "next-router-segment-prefetch",
] as const;

export type HomeCacheInput = {
  method: string;
  pathname: string;
  /** `URL.search` — `?lang=ru` yoki bo'sh. */
  search: string;
  cookieHeader: string | null;
  hasRscHint: boolean;
};

export type HomeCacheDecision = {
  /** GET/HEAD `/` query va RSC'siz. */
  isHomeDocument: boolean;
  /** CDN saqlashi mumkin. */
  cacheable: boolean;
  /** `null` — bu so'rov bosh sahifa hujjati emas, tegilmasin. */
  cacheControl: string | null;
  assignExperiments: boolean;
  forceDefaultLocale: boolean;
};

function cookieHas(header: string | null, name: string): boolean {
  if (!header) return false;
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(?:^|;\\s*)${escaped}=`).test(header);
}

export function homeCacheMark(
  decision: HomeCacheDecision,
): typeof HOME_CACHE_MARK_GUEST | typeof HOME_CACHE_MARK_PRIVATE | null {
  if (decision.cacheable) return HOME_CACHE_MARK_GUEST;
  if (decision.cacheControl === HOME_CACHE_PRIVATE) return HOME_CACHE_MARK_PRIVATE;
  return null;
}

export function requestHasRscHint(headers: {
  get(name: string): string | null;
}): boolean {
  return RSC_HINTS.some((name) => {
    const value = headers.get(name);
    return value !== null && value !== "";
  });
}

export function homeCacheDecision(input: HomeCacheInput): HomeCacheDecision {
  const method = input.method.toUpperCase();
  const isGet = method === "GET" || method === "HEAD";
  const search = input.search === "?" ? "" : input.search;
  const isHomeDocument =
    isGet &&
    input.pathname === HOME_CACHE_PATH &&
    search === "" &&
    !input.hasRscHint;

  if (!isHomeDocument) {
    return {
      isHomeDocument: false,
      cacheable: false,
      cacheControl: null,
      assignExperiments: true,
      forceDefaultLocale: false,
    };
  }

  const personalized =
    cookieHas(input.cookieHeader, SESSION_COOKIE) ||
    cookieHas(input.cookieHeader, LOCALE_COOKIE) ||
    cookieHas(input.cookieHeader, HOME_MARKUP_COOKIE);

  if (personalized) {
    return {
      isHomeDocument: true,
      cacheable: false,
      cacheControl: HOME_CACHE_PRIVATE,
      assignExperiments: true,
      forceDefaultLocale: false,
    };
  }

  return {
    isHomeDocument: true,
    cacheable: true,
    cacheControl: HOME_CACHE_GUEST,
    assignExperiments: false,
    forceDefaultLocale: true,
  };
}
