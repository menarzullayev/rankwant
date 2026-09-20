import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  DEFAULT_FORM_VARIANT,
  clampFormVariant,
} from "@/lib/theme/form";

describe("clampFormVariant", () => {
  it("keeps a known family", () => {
    expect(clampFormVariant("qator")).toBe("qator");
    expect(clampFormVariant("karta")).toBe("karta");
    expect(clampFormVariant("jadval")).toBe("jadval");
    expect(clampFormVariant("orol")).toBe("orol");
  });

  it("falls back to Maydon", () => {
    expect(clampFormVariant("chiziq")).toBe(DEFAULT_FORM_VARIANT);
    expect(clampFormVariant(undefined)).toBe("maydon");
  });
});

describe("form CSS", () => {
  const css = readFileSync(
    fileURLToPath(new URL("../../src/app/form-families.css", import.meta.url)),
    "utf8",
  );

  it("ships the five chosen families", () => {
    expect(css).toContain(".rw-fm-inp");
    expect(css).toContain('[data-form="qator"]');
    expect(css).toContain('[data-form="karta"]');
    expect(css).toContain('[data-form="jadval"]');
    expect(css).toContain('[data-form="orol"]');
    expect(css).toContain("backdrop-filter: blur(10px)");
    expect(css).toContain("11.5rem");
  });
});
