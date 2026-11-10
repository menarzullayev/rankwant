import { afterEach, describe, expect, it } from "vitest";

import { registerVariant, setVariantResolver } from "@rankwant/shared/i18n";

import {
  alphabetCookieLine,
  alphabetFor,
  alphabetFromCookieHeader,
  parseAlphabet,
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
