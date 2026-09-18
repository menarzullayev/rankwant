import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DEFAULT_LOCALE,
  LOCALES,
  fill,
  intlLocale,
  isLocale,
  localNameInfo,
} from "@/i18n/messages";

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

// Content names (topic, skill) live in three columns only: uz/ru/en. Every
// other locale shows the Uzbek text, and the UI must say so — otherwise a
// `zh` reader takes Uzbek for Chinese. The marker is driven by `.locale`,
// so the contract below is what decides whether the badge appears.
describe("localNameInfo — which text is a fallback", () => {
  const skill = { name_uz: "Reyting", name_ru: "Рейтинг", name_en: "Rating" };

  it("marks every locale without a name column as a fallback", () => {
    for (const locale of ["kk", "ky", "tg", "kaa", "tr", "zh", "es"] as const) {
      const info = localNameInfo(skill, locale);
      expect(info.text, locale).toBe("Reyting");
      expect(info.locale, locale).toBeNull();
      expect(info.source, locale).toBe(DEFAULT_LOCALE);
    }
  });

  it("uses the translated column when it has text", () => {
    expect(localNameInfo(skill, "ru")).toEqual({ text: "Рейтинг", locale: "ru", source: "ru" });
    expect(localNameInfo(skill, "en")).toEqual({ text: "Rating", locale: "en", source: "en" });
  });

  // Uzbek reading Uzbek is the correct answer, not a fallback. Marking it
  // would put a `uz` chip on the Uzbek site, where it means nothing.
  it("does not call Uzbek its own fallback", () => {
    const info = localNameInfo(skill, DEFAULT_LOCALE);
    expect(info.text).toBe("Reyting");
    expect(info.locale).toBe(DEFAULT_LOCALE);
    expect(info.source).toBe(DEFAULT_LOCALE);
  });

  it("still marks ru/en as a fallback when their column is empty", () => {
    const blank = { name_uz: "Reyting", name_ru: "", name_en: "" };
    expect(localNameInfo(blank, "ru").locale).toBeNull();
    expect(localNameInfo(blank, "en").locale).toBeNull();
  });
});
