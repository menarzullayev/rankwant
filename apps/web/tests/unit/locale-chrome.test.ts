import { beforeAll, describe, expect, it } from "vitest";

import { LOCALES, registerMessages, t, type Locale } from "@/i18n/messages";
import { en } from "@/i18n/locales/en";
import { es } from "@/i18n/locales/es";
import { kaa } from "@/i18n/locales/kaa";
import { kk } from "@/i18n/locales/kk";
import { ky } from "@/i18n/locales/ky";
import { ru } from "@/i18n/locales/ru";
import { tg } from "@/i18n/locales/tg";
import { tr } from "@/i18n/locales/tr";
import { uz } from "@/i18n/locales/uz";
import { zh } from "@/i18n/locales/zh";

const DICTS = { uz, kaa, ru, en, kk, ky, tg, tr, zh, es } as const;

/** Chrome strings drawn on every page — a raw key here is the 2026-09-19 bug. */
const CHROME_KEYS = [
  "nav.menu",
  "nav.main",
  "nav.close",
  "nav.problems",
  "locale.switchLabel",
  "locale.auto",
  "locale.group.core",
  "auth.login",
  "header.search",
] as const;

beforeAll(() => {
  for (const locale of LOCALES) {
    registerMessages(locale, DICTS[locale]);
  }
});

describe("chrome strings in all ten locales", () => {
  it("lists every UI locale exactly once", () => {
    expect([...LOCALES].sort()).toEqual(
      (Object.keys(DICTS) as Locale[]).slice().sort(),
    );
  });

  it("never renders a chrome property name", () => {
    for (const locale of LOCALES) {
      for (const key of CHROME_KEYS) {
        const text = t(locale, key);
        expect(text, `${locale} ${key}`).not.toBe(key);
        expect(text, `${locale} ${key}`).not.toBe("");
      }
    }
  });
});
