import { describe, expect, it } from "vitest";

import { blend, contrast, parseColor, parseRgba } from "@/lib/theme/color";

/** `globals.css` dagi haqiqiy token qiymatlari (2026-09-18 da o'lchangan). */
const GLASS_GROUND = "linear-gradient(135deg, #341d65 0%, #15376c 55%, #0c5151 100%) fixed";
const GLASS_SURFACE = "rgba(0, 0, 0, .62)";

describe("parseColor", () => {
  // Bu uch shakl 2026-09-18 gacha `null` qaytarardi va `glass`/`swiss`
  // uslublarida accent tanlash o'lik edi: panel kontrastni o'lchay
  // olmasdi-yu, buni «AA dan o'tmadi» deb ko'rsatardi.
  it("reads the shapes the styles actually use", () => {
    expect(parseColor("#fff")).toEqual([255, 255, 255]);
    expect(parseColor("#ffffff14")?.slice(0, 3)).toEqual([255, 255, 255]);
    expect(parseColor(GLASS_GROUND)).toEqual([0x34, 0x1d, 0x65]);
    expect(parseColor(GLASS_SURFACE)).toEqual([0, 0, 0]);
    expect(parseColor("#0a061ab8")).toEqual([0x0a, 0x06, 0x1a]);
  });

  it("keeps the old shapes working", () => {
    expect(parseColor("#22763e")).toEqual([0x22, 0x76, 0x3e]);
    expect(parseColor("rgb(18, 52, 86)")).toEqual([18, 52, 86]);
  });

  it("returns null for anything it cannot read", () => {
    for (const value of ["", "none", "#12", "#1234567", "var(--rw-ground)", "url(x.png)"]) {
      expect(parseColor(value), value).toBeNull();
    }
  });

  it("reads the alpha channel", () => {
    expect(parseRgba("#ffffff14")?.[3]).toBeCloseTo(0.078, 2);
    expect(parseRgba("rgba(0, 0, 0, .62)")?.[3]).toBeCloseTo(0.62, 2);
    expect(parseRgba("rgb(1 2 3 / 50%)")?.[3]).toBeCloseTo(0.5, 2);
    expect(parseRgba("#abc")?.[3]).toBe(1);
  });
});

describe("blend", () => {
  // Shaffof sirt o'z rangi bilan emas, FON ustidagi ko'rinishi bilan
  // o'lchanishi kerak: 62% qora oq fonda kulrang, qora emas.
  it("puts a translucent surface on its ground", () => {
    const onWhite = blend([0, 0, 0, 0.62], [255, 255, 255]);
    expect(onWhite[0]).toBeCloseTo(96.9, 1);
    // Oq fondagi 62% qora — kulrang: oq bilan kontrasti 21 emas, ~6.
    expect(contrast(onWhite, [255, 255, 255])).toBeLessThan(
      contrast([0, 0, 0], [255, 255, 255]),
    );
  });

  it("is what parseColor does when given a ground", () => {
    const ground = parseColor(GLASS_GROUND) ?? [0, 0, 0];
    const surface = parseColor(GLASS_SURFACE, ground);
    expect(surface).not.toEqual([0, 0, 0]);
    expect(surface?.[2]).toBeCloseTo(0x65 * 0.38, 0);
  });
});
