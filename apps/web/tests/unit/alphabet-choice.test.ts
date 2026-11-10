import { afterEach, describe, expect, it } from "vitest";

import { registerVariant, setVariantResolver } from "@rankwant/shared/i18n";

import {
  alphabetCookieLine,
  alphabetFor,
  alphabetFromCookieHeader,
  inReaderAlphabet,
  parseAlphabet,
  setAlphabetResolver,
} from "@/i18n/alphabet";
import { registerMessages, resetRegistry, t } from "@/i18n/messages";

// ADR-0059: the reader's alphabet choice and the per-request dictionary.

describe("alphabet choice", () => {
  it("defaults to the new alphabet", () => {
    expect(parseAlphabet(undefined)).toBe("new");
    expect(parseAlphabet("anything")).toBe("new");
    expect(parseAlphabet("old")).toBe("old");
  });

  it("reads the cookie from a raw header", () => {
    expect(alphabetFromCookieHeader("rw_locale=uz; rw_alphabet=old; x=1")).toBe("old");
    expect(alphabetFromCookieHeader("rw_locale=uz")).toBe("new");
    expect(alphabetFromCookieHeader(null)).toBe("new");
  });

  it("applies to Uzbek only", () => {
    expect(alphabetFor("uz", "old")).toBe("old");
    expect(alphabetFor("ru", "old")).toBe("new");
  });

  it("clears the cookie for the default", () => {
    expect(alphabetCookieLine("new")).toContain("max-age=0");
    expect(alphabetCookieLine("old")).toMatch(/^rw_alphabet=old;/);
  });
});

describe("variant dictionaries", () => {
  afterEach(() => {
    setVariantResolver(undefined);
    resetRegistry();
  });

  it("t() reads the variant the current request asks for", () => {
    registerMessages("uz", { "nav.problems": "Şart" } as never);
    registerVariant("uz", "old", { "nav.problems": "Shart" });
    let want: string | null = null;
    setVariantResolver((locale) => (locale === "uz" ? want : null));
    expect(t("uz", "nav.problems")).toBe("Şart");
    want = "old";
    expect(t("uz", "nav.problems")).toBe("Shart");
    want = "missing";
    expect(t("uz", "nav.problems")).toBe("Şart");
  });
});

describe("content in the reader's alphabet", () => {
  afterEach(() => setAlphabetResolver(undefined));

  it("converts Uzbek text only", async () => {
    expect(inReaderAlphabet("Shart va o'qish", "uz")).toBe("Şart va öqiş");
    // An English or Russian text keeps every letter.
    expect(inReaderAlphabet("Should we check it?", "en")).toBe("Should we check it?");
    expect(inReaderAlphabet("Shart", null)).toBe("Shart");
  });

  it("follows the request's choice on the server", () => {
    setAlphabetResolver(() => "old");
    expect(inReaderAlphabet("Şart va öqiş", "uz")).toBe("Shart va oʻqish");
    setAlphabetResolver(() => "new");
    expect(inReaderAlphabet("Shart", "uz")).toBe("Şart");
  });

  it("keeps code and formulas as written", () => {
    expect(inReaderAlphabet("`chop()` va $s_h$ ni o'qing", "uz")).toBe("`chop()` va $s_h$ ni öqing");
  });
});
