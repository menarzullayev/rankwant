import { afterEach, describe, expect, it, vi } from "vitest";
import { DEFAULT_LOCALE, LOCALES, fill, intlLocale, isLocale } from "@/i18n/messages";

describe("isLocale", () => {
  it("accepts every supported locale and nothing else", () => {
    for (const locale of LOCALES) expect(isLocale(locale)).toBe(true);
    expect(isLocale("xx")).toBe(false);
    expect(isLocale("")).toBe(false);
    expect(isLocale(undefined)).toBe(false);
  });
});

describe("fill", () => {
  it("replaces known placeholders and keeps unknown ones visible", () => {
    expect(fill("{n} ta masala, {who}", { n: 3 })).toBe("3 ta masala, {who}");
  });
});

describe("intlLocale", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ICU tables differ between Node and browsers, so the resolver is stubbed:
  // the contract is "fall back when ICU silently resolves to another language".
  // `function`, not an arrow: the code under test calls `new Intl.DateTimeFormat`.
  const resolveTo = (resolved: string) =>
    vi.spyOn(Intl, "DateTimeFormat").mockImplementation(function () {
      return { resolvedOptions: () => ({ locale: resolved }) } as unknown as Intl.DateTimeFormat;
    });

  it("keeps a locale that ICU actually supports", () => {
    resolveTo("ru-RU");
    expect(intlLocale("ru")).toBe("ru");
  });

  it("falls back when ICU quietly substitutes English (kaa, ky, tg)", () => {
    resolveTo("en-US");
    expect(intlLocale("kaa")).toBe(DEFAULT_LOCALE);
  });

  it("falls back when ICU rejects the tag outright", () => {
    vi.spyOn(Intl, "DateTimeFormat").mockImplementation(function () {
      throw new RangeError("Incorrect locale information provided");
    });
    expect(intlLocale("tg")).toBe(DEFAULT_LOCALE);
  });
});
