import { runInNewContext } from "node:vm";
import { describe, expect, it, vi } from "vitest";

// `messages.server.ts` is marked server-only; outside Next that marker throws.
vi.mock("server-only", () => ({}));

const { dictionaryScript, dictionaryUrl } = await import("@/i18n/messages.server");
const { uz } = await import("@/i18n/locales/uz");
const { ru } = await import("@/i18n/locales/ru");
const { toNewAlphabet } = await import("@rankwant/shared/alphabet");

/** Uzbek as the default file carries it: the new alphabet (ADR-0059). */
const uzNew = Object.fromEntries(Object.entries(uz).map(([key, text]) => [key, toNewAlphabet(text)]));

/** A bare global scope like a browser tab's, where `self` is the global. */
function tab(extra: Record<string, unknown> = {}): Record<string, unknown> {
  const scope: Record<string, unknown> = { ...extra };
  scope.self = scope;
  return scope;
}

// The dictionary left the page on 2026-09-18: it is a file now, and this is
// the code that file runs in the browser.
describe("dictionary file", () => {
  it("registers Uzbek in the new alphabet, and the source as the old one", () => {
    const scope = tab();
    runInNewContext(dictionaryScript("uz"), scope);
    const registry = scope.__rwMessages as Map<string, unknown>;
    expect(registry.get("uz")).toEqual(uzNew);
    const old = tab();
    runInNewContext(dictionaryScript("uz", "old"), old);
    expect((old.__rwMessages as Map<string, unknown>).get("uz")).toEqual(uz);
  });

  it("registers other languages exactly as written", () => {
    const scope = tab();
    runInNewContext(dictionaryScript("ru"), scope);
    expect((scope.__rwMessages as Map<string, unknown>).get("ru")).toEqual(ru);
  });

  it("joins the registry the app code made first, keeping what it holds", () => {
    const existing = new Map<string, unknown>([["ru", ru]]);
    const scope = tab({ __rwMessages: existing });
    runInNewContext(dictionaryScript("uz"), scope);
    expect(scope.__rwMessages).toBe(existing);
    expect(existing.get("uz")).toEqual(uzNew);
    expect(existing.get("ru")).toBe(ru);
  });

  it("gives every language its own address with a content hash", () => {
    expect(dictionaryUrl("uz")).toMatch(/^\/i18n\/uz\.js\?v=[0-9a-f]{12}$/);
    expect(dictionaryUrl("ru")).toMatch(/^\/i18n\/ru\.js\?v=[0-9a-f]{12}$/);
    expect(dictionaryUrl("uz").split("?v=")[1]).not.toBe(dictionaryUrl("ru").split("?v=")[1]);
    expect(dictionaryUrl("uz", "old")).toMatch(/^\/i18n\/uz-old\.js\?v=[0-9a-f]{12}$/);
    expect(dictionaryUrl("ru", "old")).toBe(dictionaryUrl("ru"));
  });
});
