import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  DEFAULT_OVERLAY_VARIANT,
  clampOverlayVariant,
  overlayPlace,
  pickFlipSide,
  placeNear,
} from "@/lib/theme/overlay";

describe("clampOverlayVariant", () => {
  it("keeps a known family", () => {
    expect(clampOverlayVariant("soyabon")).toBe("soyabon");
    expect(clampOverlayVariant("projektor")).toBe("projektor");
    expect(clampOverlayVariant("orol")).toBe("orol");
  });

  it("falls back to Qog'oz", () => {
    expect(clampOverlayVariant("latta")).toBe(DEFAULT_OVERLAY_VARIANT);
    expect(clampOverlayVariant(undefined)).toBe("qogoz");
  });
});

describe("overlayPlace", () => {
  it("anchors Soyabon everything", () => {
    expect(overlayPlace("soyabon", "confirm")).toBe("anchor");
    expect(overlayPlace("soyabon", "modal")).toBe("anchor");
    expect(overlayPlace("soyabon", "menu")).toBe("anchor");
  });

  it("centres Projektor menus and Qog'oz confirms", () => {
    expect(overlayPlace("projektor", "menu")).toBe("center");
    expect(overlayPlace("qogoz", "confirm")).toBe("center");
    expect(overlayPlace("orol", "menu")).toBe("anchor");
  });
});

describe("placeNear", () => {
  const view = { width: 400, height: 300 };
  const anchor = {
    left: 300,
    top: 250,
    right: 340,
    bottom: 280,
    width: 40,
    height: 30,
  };

  it("keeps the panel inside the viewport", () => {
    const pos = placeNear(anchor, { width: 180, height: 80 }, view, "menu");
    expect(pos.x).toBeGreaterThanOrEqual(8);
    expect(pos.y).toBeGreaterThanOrEqual(8);
    expect(pos.x + 180).toBeLessThanOrEqual(400 - 8);
    expect(pos.y + 80).toBeLessThanOrEqual(300 - 8);
  });

  it("sits above the trigger when asked", () => {
    const roomy = {
      left: 40,
      top: 120,
      right: 80,
      bottom: 150,
      width: 40,
      height: 30,
    };
    const pos = placeNear(roomy, { width: 80, height: 24 }, view, "above");
    expect(pos.y).toBe(120 - 24 - 6);
  });

  it("flips a cramped corner toward open space", () => {
    const corner = {
      left: 350,
      top: 250,
      right: 390,
      bottom: 280,
      width: 40,
      height: 30,
    };
    expect(pickFlipSide(corner, { width: 120, height: 40 }, view)).toBe("left");
  });
});

describe("overlay CSS", () => {
  const css = readFileSync(
    fileURLToPath(new URL("../../src/app/globals.css", import.meta.url)),
    "utf8",
  );

  it("ships the four chosen families", () => {
    expect(css).toContain('.rw-ov-panel');
    expect(css).toContain('[data-overlay="soyabon"]');
    expect(css).toContain('[data-overlay="projektor"]');
    expect(css).toContain('[data-overlay="orol"]');
    expect(css).toContain("backdrop-filter: blur(10px)");
    expect(css).toContain("999px");
  });
});
