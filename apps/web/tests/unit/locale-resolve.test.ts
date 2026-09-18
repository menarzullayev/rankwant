import { describe, expect, it } from "vitest";
import { fromAcceptLanguage, resolveLocale } from "@/i18n/resolve";

// The order below is an owner decision (S5, 2026-09-19): a shared link has to
// carry its own language, because the device it lands on may have picked
// another one. Getting this backwards silently overrides a person's choice,
// so every step of the chain is pinned here.
describe("resolveLocale", () => {
  it("lets the shared link win over the device cookie", () => {
    expect(resolveLocale("ru", "uz", null)).toEqual({ locale: "ru", auto: false });
  });

  it("falls back to the cookie when there is no link", () => {
    expect(resolveLocale(null, "en", "ru,en;q=0.8")).toEqual({
      locale: "en",
      auto: false,
    });
  });

  it("treats the auto marker as automatic, not as a locale", () => {
    expect(resolveLocale(null, "auto", "zh,en;q=0.8")).toEqual({
      locale: "zh",
      auto: true,
    });
  });

  it("ignores an unknown param instead of blanking the page", () => {
    expect(resolveLocale("xx", "ru", null)).toEqual({ locale: "ru", auto: false });
  });

  it("ignores a broken cookie and still honours the link", () => {
    expect(resolveLocale("kaa", "not-a-locale", "ru")).toEqual({
      locale: "kaa",
      auto: false,
    });
  });

  it("detects the language when nothing was chosen", () => {
    expect(resolveLocale(null, null, "ru-RU,ru;q=0.9,en;q=0.8")).toEqual({
      locale: "ru",
      auto: true,
    });
  });

  it("defaults to uz when even the header says nothing useful", () => {
    expect(resolveLocale(null, null, null)).toEqual({ locale: "uz", auto: true });
    expect(resolveLocale(null, null, "*")).toEqual({ locale: "uz", auto: true });
  });
});

describe("fromAcceptLanguage", () => {
  it("ranks by q, not by position", () => {
    expect(fromAcceptLanguage("en;q=0.3,ru;q=0.9")).toBe("ru");
  });

  it("drops a tag the site does not speak and keeps looking", () => {
    expect(fromAcceptLanguage("de-DE,fr;q=0.8,ky;q=0.5")).toBe("ky");
  });

  it("collapses a regional tag onto its base language", () => {
    expect(fromAcceptLanguage("uz-Latn-UZ,uz;q=0.9")).toBe("uz");
  });

  it("skips a zero-quality entry", () => {
    expect(fromAcceptLanguage("ru;q=0,en;q=0.7")).toBe("en");
  });
});
