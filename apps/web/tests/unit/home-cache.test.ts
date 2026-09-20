import { describe, expect, it } from "vitest";

import {
  HOME_CACHE_GUEST,
  HOME_CACHE_LOCALE,
  HOME_CACHE_MARK_GUEST,
  HOME_CACHE_MARK_PRIVATE,
  HOME_CACHE_PRIVATE,
  homeCacheDecision,
  homeCacheMark,
  requestHasRscHint,
  SESSION_COOKIE,
} from "@/lib/home-cache";

const guestHome = {
  method: "GET",
  pathname: "/",
  search: "",
  cookieHeader: null,
  hasRscHint: false,
} as const;

describe("homeCacheDecision", () => {
  it("lets a cookieless GET / be cached for 30s at the CDN", () => {
    const d = homeCacheDecision(guestHome);
    expect(d).toEqual({
      isHomeDocument: true,
      isGuestDocument: true,
      cacheable: true,
      cacheControl: HOME_CACHE_GUEST,
      assignExperiments: false,
      forceDefaultLocale: true,
    });
    expect(HOME_CACHE_GUEST).toBe(
      "public, s-maxage=30, stale-while-revalidate=86400",
    );
    expect(HOME_CACHE_LOCALE).toBe("uz");
    expect(homeCacheMark(d)).toBe(HOME_CACHE_MARK_GUEST);
  });

  it("treats HEAD the same as GET", () => {
    expect(homeCacheDecision({ ...guestHome, method: "HEAD" }).cacheable).toBe(
      true,
    );
  });

  it("keeps Cloudflare bot cookies from busting the guest cache", () => {
    const d = homeCacheDecision({
      ...guestHome,
      cookieHeader: "__cf_bm=x; _cfuvid=y",
    });
    expect(d.cacheable).toBe(true);
    expect(d.cacheControl).toBe(HOME_CACHE_GUEST);
  });

  it("does not cache a logged-in homepage", () => {
    const d = homeCacheDecision({
      ...guestHome,
      cookieHeader: `${SESSION_COOKIE}=abc123`,
    });
    expect(d.cacheable).toBe(false);
    expect(d.cacheControl).toBe(HOME_CACHE_PRIVATE);
    expect(HOME_CACHE_PRIVATE).toBe("private, no-store");
    expect(homeCacheMark(d)).toBe(HOME_CACHE_MARK_PRIVATE);
  });

  it("does not cache a guest who already picked a language", () => {
    const d = homeCacheDecision({
      ...guestHome,
      cookieHeader: "rw_locale=ru",
    });
    expect(d.cacheable).toBe(false);
    expect(d.cacheControl).toBe(HOME_CACHE_PRIVATE);
  });

  it("does not cache markup-personalized HTML", () => {
    const d = homeCacheDecision({
      ...guestHome,
      cookieHeader: "rw:markup=%7B%7D",
    });
    expect(d.cacheable).toBe(false);
    expect(d.cacheControl).toBe(HOME_CACHE_PRIVATE);
  });

  it("leaves /?lang= and other paths alone", () => {
    expect(
      homeCacheDecision({ ...guestHome, search: "?lang=ru" }).cacheControl,
    ).toBeNull();
    expect(
      homeCacheDecision({ ...guestHome, pathname: "/problems", search: "?page=2" })
        .cacheControl,
    ).toBeNull();
    expect(
      homeCacheDecision({ ...guestHome, method: "POST" }).cacheControl,
    ).toBeNull();
  });

  it("caches cookieless /problems in the request locale, not forced uz", () => {
    const d = homeCacheDecision({ ...guestHome, pathname: "/problems" });
    expect(d.cacheable).toBe(true);
    expect(d.forceDefaultLocale).toBe(false);
    expect(d.assignExperiments).toBe(false);
    expect(d.cacheControl).toBe(HOME_CACHE_GUEST);
  });

  it("does not cache /problems?lang= — query stays off the CDN key", () => {
    expect(
      homeCacheDecision({
        ...guestHome,
        pathname: "/problems",
        search: "?lang=ru",
      }).cacheControl,
    ).toBeNull();
  });

  it("does not cache a logged-in /problems list", () => {
    const d = homeCacheDecision({
      ...guestHome,
      pathname: "/problems",
      cookieHeader: `${SESSION_COOKIE}=abc123`,
    });
    expect(d.cacheable).toBe(false);
    expect(d.cacheControl).toBe(HOME_CACHE_PRIVATE);
  });

  it("caches cookieless login and register tabs", () => {
    for (const search of ["", "?tab=login", "?tab=register", "?tab=reset-password"]) {
      const d = homeCacheDecision({
        ...guestHome,
        pathname: "/login",
        search,
      });
      expect(d.cacheable).toBe(true);
      expect(d.assignExperiments).toBe(false);
      expect(d.isHomeDocument).toBe(false);
    }
    expect(
      homeCacheDecision({ ...guestHome, pathname: "/register" }).cacheable,
    ).toBe(true);
    expect(
      homeCacheDecision({ ...guestHome, pathname: "/terms" }).cacheable,
    ).toBe(true);
    expect(
      homeCacheDecision({ ...guestHome, pathname: "/privacy" }).cacheable,
    ).toBe(true);
  });

  it("does not cache login with extra query or a session", () => {
    expect(
      homeCacheDecision({
        ...guestHome,
        pathname: "/login",
        search: "?tab=login&next=/",
      }).cacheControl,
    ).toBeNull();
    expect(
      homeCacheDecision({
        ...guestHome,
        pathname: "/login",
        search: "?tab=login",
        cookieHeader: `${SESSION_COOKIE}=abc`,
      }).cacheControl,
    ).toBe(HOME_CACHE_PRIVATE);
  });

  it("does not treat an RSC/prefetch navigation as the document", () => {
    const d = homeCacheDecision({ ...guestHome, hasRscHint: true });
    expect(d.isHomeDocument).toBe(false);
    expect(d.cacheControl).toBeNull();
  });
});

describe("requestHasRscHint", () => {
  it("sees the RSC and prefetch headers Next sends", () => {
    const headers = new Headers({ rsc: "1" });
    expect(requestHasRscHint(headers)).toBe(true);
    expect(requestHasRscHint(new Headers({ "next-router-prefetch": "1" }))).toBe(
      true,
    );
    expect(requestHasRscHint(new Headers())).toBe(false);
  });
});
