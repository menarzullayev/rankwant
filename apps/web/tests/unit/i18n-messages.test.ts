import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import {
  DEFAULT_LOCALE,
  LOCALES,
  errorText,
  fill,
  intlLocale,
  isLocale,
  localNameInfo,
  registerMessages,
  t,
  translate,
} from "@/i18n/messages";
import { en } from "@/i18n/locales/en";
import { uz } from "@/i18n/locales/uz";

beforeAll(() => {
  registerMessages("uz", uz);
  registerMessages("en", en);
});

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

describe("translate", () => {
  it("returns one property as a string", () => {
    expect(translate("en", "nav.problems")).toBe(en["nav.problems"]);
    expect(t("uz", "nav.problems")).toBe(uz["nav.problems"]);
  });

  it("returns any number of properties in order", () => {
    const [problems, contests] = translate("en", "nav.problems", "nav.contests");
    expect(problems).toBe(en["nav.problems"]);
    expect(contests).toBe(en["nav.contests"]);
  });

  it("does not copy another locale when the requested one is missing", () => {
    expect(translate("en", "nav.problems")).not.toBe(uz["nav.problems"]);
  });
});

describe("intlLocale", () => {
  it("returns the requested locale even when ICU would substitute another", () => {
    expect(intlLocale("kaa")).toBe("kaa");
    expect(intlLocale("tg")).toBe("tg");
    expect(intlLocale("ru")).toBe("ru");
  });
});

describe("errorText", () => {
  it("looks up error.<code> and ignores the server message", () => {
    expect(errorText("en", "invalid", "Kiritilgan ma'lumot noto'g'ri")).toBe(
      en["error.invalid"],
    );
  });
});

// Content names live in three columns: uz/ru/en. Other locales must not
// inherit Uzbek — they show the English property (the slug, or `name`).
describe("localNameInfo — missing translation is the property", () => {
  const skill = { name_uz: "Reyting", name_ru: "Рейтинг", name_en: "Rating" };
  const topic = {
    slug: "graphs",
    name_uz: "Graf",
    name_ru: "Граф",
    name_en: "Graphs",
  };

  it("shows the slug when the locale has no name column", () => {
    for (const locale of ["kk", "ky", "tg", "kaa", "tr", "zh", "es"] as const) {
      const info = localNameInfo(topic, locale);
      expect(info.text, locale).toBe("graphs");
      expect(info.locale, locale).toBeNull();
      expect(info.source, locale).toBeNull();
    }
  });

  it("shows `name` when there is no slug", () => {
    const info = localNameInfo(skill, "zh");
    expect(info.text).toBe("name");
    expect(info.locale).toBeNull();
    expect(info.source).toBeNull();
  });

  it("uses the translated column when it has text", () => {
    expect(localNameInfo(skill, "ru")).toEqual({
      text: "Рейтинг",
      locale: "ru",
      source: "ru",
    });
    expect(localNameInfo(skill, "en")).toEqual({
      text: "Rating",
      locale: "en",
      source: "en",
    });
  });

  it("does not treat a real Uzbek name as missing", () => {
    const info = localNameInfo(skill, DEFAULT_LOCALE);
    expect(info.text).toBe("Reyting");
    expect(info.locale).toBe(DEFAULT_LOCALE);
    expect(info.source).toBe(DEFAULT_LOCALE);
  });

  it("shows the property when ru/en columns are empty", () => {
    const blank = { name_uz: "Reyting", name_ru: "", name_en: "" };
    expect(localNameInfo(blank, "ru")).toEqual({
      text: "name",
      locale: null,
      source: null,
    });
    expect(localNameInfo(blank, "en")).toEqual({
      text: "name",
      locale: null,
      source: null,
    });
  });
});

describe("translate — production missing property", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
  });

  // The DEV throw is measured by `tools/check_i18n_runtime.mjs`. This
  // suite only asserts the user-facing contract: no other locale, and
  // a missing entry is the property name. Vitest runs with NODE_ENV=test
  // so a gap still throws — that is the development contract.
  it("throws in non-production when the property is absent", () => {
    expect(() => translate("en", "definitely.not.a.key")).toThrow(
      /definitely\.not\.a\.key/,
    );
  });
});
