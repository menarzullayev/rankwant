import { describe, expect, it } from "vitest";
import {
  hrefForLocale,
  localeAlternates,
  sitemapLanguageAlternates,
} from "@/i18n/locale-alternates";

describe("localeAlternates", () => {
  it("keeps the default locale on the clean path", () => {
    expect(hrefForLocale("/", "uz")).toBe("/");
    expect(localeAlternates("/", null).canonical).toBe("/");
    expect(localeAlternates("/", "uz").canonical).toBe("/");
  });

  it("is self-canonical for a non-default ?lang=", () => {
    expect(localeAlternates("/", "ru").canonical).toBe("/?lang=ru");
    expect(localeAlternates("/problems/a-plus-b", "en").canonical).toBe(
      "/problems/a-plus-b?lang=en",
    );
  });

  it("lists every locale plus x-default", () => {
    const { languages } = localeAlternates("/about", null);
    expect(languages["x-default"]).toBe("/about");
    expect(languages.uz).toBe("/about");
    expect(languages.ru).toBe("/about?lang=ru");
    expect(languages.en).toBe("/about?lang=en");
  });

  it("ignores an unknown lang param instead of minting a URL", () => {
    expect(localeAlternates("/", "xx").canonical).toBe("/");
  });
});

describe("sitemapLanguageAlternates", () => {
  const abs = (href: string) => `https://rankwant.uz${href === "/" ? "/" : href}`;

  it("keeps one absolute URL per locale plus x-default", () => {
    const languages = sitemapLanguageAlternates("/problems/a-plus-b", (href) =>
      `https://rankwant.uz${href}`,
    );
    expect(languages["x-default"]).toBe("https://rankwant.uz/problems/a-plus-b");
    expect(languages.uz).toBe("https://rankwant.uz/problems/a-plus-b");
    expect(languages.ru).toBe("https://rankwant.uz/problems/a-plus-b?lang=ru");
  });

  it("does not mint a second <url> for the default locale", () => {
    const languages = sitemapLanguageAlternates("/", abs);
    expect(languages.uz).toBe(languages["x-default"]);
    expect(languages.ru).toBe("https://rankwant.uz/?lang=ru");
  });
});
