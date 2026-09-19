import { LOCALE_COOKIE } from "@/i18n/locale-params";

/**
 * Mehmon HTML keshi — 50k qarorlari (2026-09-19): GET `/`, `/login`,
 * `/register`, `/terms`, `/privacy`. Faqat mehmon, origin Cache-Control,
 * s-maxage=30 + stale-while-revalidate. `rw_exp` bu yo'llarda
 * yozilmaydi — Set-Cookie CDN ni o'ldiradi.
 *
 * Next.js layout `cookies()` o'qiydi va o'zi `private, no-store` yozadi.
 * Shu modul qarorni aytadi; `proxy.ts` va `instrumentation.ts` uni
 * javobga qo'yadi. Cloudflare origin header'ga rioya qiladi.
 */

/** Django standart sessiya cookie — `SESSION_COOKIE_NAME` o'zgarmagan. */
export const SESSION_COOKIE = "sessionid";

/** Markup HTML tuzilishini o'zgartiradi (`prefs.ts` dagi `MARKUP_COOKIE`). */
export const HOME_MARKUP_COOKIE = "rw:markup";

/** Keshlangan mehmon HTML doim shu tilda — `Accept-Language` zaharlamasligi uchun. */
export const HOME_CACHE_LOCALE = "uz";

export const HOME_CACHE_PATH = "/";

/** Login tab — `page.tsx` `tabOf` bilan bir xil. */
export const GUEST_LOGIN_TABS = new Set([
  "",
  "login",
  "register",
  "reset-password",
]);

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
  /** GET/HEAD mehmon HTML (home/login/huquqiy). */
  isGuestDocument: boolean;
  /** CDN saqlashi mumkin. */
  cacheable: boolean;
  /** `null` — bu so'rov boshqariladigan hujjat emas, tegilmasin. */
  cacheControl: string | null;
  assignExperiments: boolean;
  forceDefaultLocale: boolean;
};

function cookieHas(header: string | null, name: string): boolean {
  if (!header) return false;
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(?:^|;\\s*)${escaped}=`).test(header);
}

function isLoginTabSearch(search: string): boolean {
  if (search === "") return true;
  const params = new URLSearchParams(
    search.startsWith("?") ? search.slice(1) : search,
  );
  const keys = [...params.keys()];
  if (keys.length !== 1 || keys[0] !== "tab") return false;
  return GUEST_LOGIN_TABS.has(params.get("tab") ?? "");
}

export function isGuestCachePath(pathname: string, search: string): boolean {
  if (pathname === "/" || pathname === "/terms" || pathname === "/privacy") {
    return search === "";
  }
  if (pathname === "/register") return search === "";
  if (pathname === "/login") return isLoginTabSearch(search);
  return false;
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
  const isGuestDocument =
    isGet && !input.hasRscHint && isGuestCachePath(input.pathname, search);

  if (!isGuestDocument) {
    return {
      isHomeDocument: false,
      isGuestDocument: false,
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
      isHomeDocument,
      isGuestDocument: true,
      cacheable: false,
      cacheControl: HOME_CACHE_PRIVATE,
      assignExperiments: true,
      forceDefaultLocale: false,
    };
  }

  return {
    isHomeDocument,
    isGuestDocument: true,
    cacheable: true,
    cacheControl: HOME_CACHE_GUEST,
    assignExperiments: false,
    forceDefaultLocale: true,
  };
}
