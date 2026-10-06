import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { lockBodyScroll, prefersReducedMotion, revealElement } from "@/lib/scroll";

type Fake = {
  body: { style: { overflow: string } };
  documentElement: { dataset: { motion?: string } };
  getElementById: (id: string) => unknown;
};

let fake: Fake;
let reduced = false;

beforeEach(() => {
  fake = {
    body: { style: { overflow: "" } },
    documentElement: { dataset: {} },
    getElementById: () => null,
  };
  reduced = false;
  vi.stubGlobal("document", fake);
  vi.stubGlobal("window", { matchMedia: () => ({ matches: reduced }) });
});

afterEach(() => vi.unstubAllGlobals());

describe("lockBodyScroll", () => {
  it("locks the page and restores what was there", () => {
    fake.body.style.overflow = "clip";
    const release = lockBodyScroll();
    expect(fake.body.style.overflow).toBe("hidden");
    release();
    expect(fake.body.style.overflow).toBe("clip");
  });

  it("stays locked until the last overlay lets go", () => {
    const drawer = lockBodyScroll();
    const palette = lockBodyScroll();
    drawer();
    expect(fake.body.style.overflow).toBe("hidden");
    palette();
    expect(fake.body.style.overflow).toBe("");
  });

  it("ignores a second release from the same overlay", () => {
    const first = lockBodyScroll();
    const second = lockBodyScroll();
    first();
    first();
    expect(fake.body.style.overflow).toBe("hidden");
    second();
    expect(fake.body.style.overflow).toBe("");
  });
});

describe("motion", () => {
  it("follows the system when the customizer says nothing", () => {
    expect(prefersReducedMotion()).toBe(false);
    reduced = true;
    expect(prefersReducedMotion()).toBe(true);
  });

  it("lets an explicit customizer level win over the system", () => {
    reduced = true;
    fake.documentElement.dataset.motion = "full";
    expect(prefersReducedMotion()).toBe(false);
    reduced = false;
    fake.documentElement.dataset.motion = "reduce";
    expect(prefersReducedMotion()).toBe(true);
  });

  it("drops the smooth request when less motion was asked for", () => {
    const calls: unknown[] = [];
    const element = { scrollIntoView: (options: unknown) => calls.push(options) };
    fake.getElementById = () => element;
    revealElement("target", { smooth: true, block: "start" });
    reduced = true;
    revealElement("target", { smooth: true });
    expect(calls).toEqual([
      { block: "start", behavior: "smooth" },
      { block: "nearest", behavior: "auto" },
    ]);
  });

  it("does nothing for an element that is not there", () => {
    expect(() => revealElement("missing")).not.toThrow();
    expect(() => revealElement(null)).not.toThrow();
  });
});
