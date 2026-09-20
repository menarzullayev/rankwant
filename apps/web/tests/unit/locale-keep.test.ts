import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  dictionaryReady,
  keepOnly,
  markDictionaryLoadForTests,
  pendingDictionaryLoads,
  resetDictionaryLoadsForTests,
} from "@/i18n/LocaleProvider";
import {
  hasMessages,
  registerMessages,
  t,
} from "@/i18n/messages";
import { en } from "@/i18n/locales/en";
import { es } from "@/i18n/locales/es";
import { ru } from "@/i18n/locales/ru";
import { uz } from "@/i18n/locales/uz";
import { zh } from "@/i18n/locales/zh";

beforeEach(() => {
  vi.stubGlobal("window", {});
  resetDictionaryLoadsForTests();
  registerMessages("uz", uz);
  registerMessages("ru", ru);
  registerMessages("zh", zh);
  registerMessages("es", es);
  registerMessages("en", en);
});

afterEach(() => {
  resetDictionaryLoadsForTests();
  vi.unstubAllGlobals();
  registerMessages("uz", uz);
  registerMessages("en", en);
});

describe("keepOnly — registry and load cache move together", () => {
  it("drops every other locale from both caches", () => {
    markDictionaryLoadForTests("ru");
    markDictionaryLoadForTests("zh");
    markDictionaryLoadForTests("es");

    keepOnly("zh");

    expect(pendingDictionaryLoads()).toEqual(["zh"]);
    expect(hasMessages("zh")).toBe(true);
    expect(hasMessages("ru")).toBe(false);
    expect(hasMessages("es")).toBe(false);
    expect(t("zh", "nav.problems")).toBe(zh["nav.problems"]);
  });

  it("lets a later visit reload after ru → zh → es → zh", () => {
    markDictionaryLoadForTests("ru");
    keepOnly("ru");
    markDictionaryLoadForTests("zh");
    keepOnly("zh");
    markDictionaryLoadForTests("es");
    keepOnly("es");

    expect(hasMessages("zh")).toBe(false);
    expect(pendingDictionaryLoads()).toEqual(["es"]);

    // Returning to zh must not see a stale resolved promise — that is
    // what left 38 raw keys on screen (measured 2026-09-19).
    expect(pendingDictionaryLoads()).not.toContain("zh");
    registerMessages("zh", zh);
    markDictionaryLoadForTests("zh");
    keepOnly("zh");
    expect(t("zh", "nav.problems")).toBe(zh["nav.problems"]);
    expect(t("zh", "locale.switchLabel")).toBe(zh["locale.switchLabel"]);
  });
});

describe("dictionaryReady — hook input stays settled when messages exist", () => {
  it("returns the same settled promise for every registered locale", async () => {
    const uzReady = dictionaryReady("uz", "/i18n/uz.js");
    const enReady = dictionaryReady("en", "/i18n/en.js");
    expect(uzReady).toBe(enReady);
    await expect(uzReady).resolves.toBeUndefined();
  });

  it("returns that same promise when there is no window (SSR)", async () => {
    vi.unstubAllGlobals();
    const server = dictionaryReady("uz", "/i18n/uz.js");
    vi.stubGlobal("window", {});
    const clientWithMessages = dictionaryReady("uz", "/i18n/uz.js");
    expect(server).toBe(clientWithMessages);
    await expect(server).resolves.toBeUndefined();
  });
});
