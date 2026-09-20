import { describe, expect, it } from "vitest";

import { KIT_FAMILY_KEYS } from "@/components/customizer/chrome";
import type { A11yPrefs, AppearancePrefs } from "@/lib/api";
import {
  TEMPLATES,
  TEMPLATE_KIT_DEFAULTS,
  TEMPLATE_LAYOUT_KEYS,
  kitMatches,
  matchTemplate,
  templateAppearance,
} from "@/lib/theme/templates";

const a11y: A11yPrefs = { vision: "normal" };

const classicPage: AppearancePrefs = {
  style: "dashboard",
  accent: null,
  font: null,
  density: "comfortable",
};

describe("D49 team template kit identity", () => {
  it("shares one kit default block with the Interfeys writer keys (D48)", () => {
    expect(Object.keys(TEMPLATE_KIT_DEFAULTS)).toEqual([...KIT_FAMILY_KEYS]);
    expect(TEMPLATE_KIT_DEFAULTS).toEqual({
      verdictStyle: "auto",
      statusStyle: "auto",
      loadingStyle: "spinner",
      overlayStyle: "qogoz",
      formStyle: "maydon",
      iconPack: "lucide",
    });
  });

  it("baseline: D19-narrow would still call circle-verdict Classic — D49 does not", () => {
    const dirty: AppearancePrefs = { ...classicPage, verdictStyle: "circle" };
    expect(dirty.style).toBe("dashboard");
    expect(dirty.font ?? null).toBe(null);
    expect(dirty.density ?? "comfortable").toBe("comfortable");
    expect(dirty.accent).toBeFalsy();
    expect(matchTemplate(dirty, a11y, "system")).toBeNull();
    expect(kitMatches(dirty)).toBe(false);
  });

  it("treats missing kit keys as the shared defaults", () => {
    expect(kitMatches(classicPage)).toBe(true);
    expect(matchTemplate(classicPage, a11y, "system")?.id).toBe("classic");
  });

  it("resets kit families when a team template is applied", () => {
    const current: AppearancePrefs = {
      style: "clay",
      accent: { hue: 140, sat: 55 },
      font: "jakarta",
      density: "spacious",
      verdictStyle: "circle",
      statusStyle: "badge",
      loadingStyle: "bars",
      overlayStyle: "orol",
      formStyle: "jadval",
      iconPack: "phosphor",
      navMode: "sidenav",
    };
    const classic = TEMPLATES.find((row) => row.id === "classic");
    expect(classic).toBeTruthy();
    const next = templateAppearance(classic!, current);
    expect(next).toMatchObject({
      style: "dashboard",
      accent: null,
      font: null,
      density: "comfortable",
      ...TEMPLATE_KIT_DEFAULTS,
      navMode: "sidenav",
    });
    expect(matchTemplate(next, a11y, "system")?.id).toBe("classic");
  });

  it("keeps apply → match identity for every built-in template", () => {
    expect(TEMPLATES).toHaveLength(8);
    for (const template of TEMPLATES) {
      const next = templateAppearance(template, {
        style: "clay",
        verdictStyle: "circle",
        iconPack: "phosphor",
      });
      const theme = template.theme ?? "system";
      expect(matchTemplate(next, a11y, theme)?.id).toBe(template.id);
    }
  });

  it("still ignores a11y motion and does not match protan as a team template", () => {
    expect(matchTemplate(classicPage, { vision: "protan" }, "system")).toBeNull();
    expect(
      matchTemplate(classicPage, { vision: "normal", motion: "off" }, "system")?.id,
    ).toBe("classic");
  });
});

describe("D50 layout chrome stays personal", () => {
  const layout: AppearancePrefs = {
    navMode: "topnav",
    navShape: "slim",
    card: "outline",
    pattern: "dots",
    fontHeading: "serif",
    size: 120,
    scale: 1.1,
    lineHeight: 1.3,
    tracking: 0.02,
    width: 1400,
  };

  it("lists the layout keys that apply and match must not own", () => {
    expect([...TEMPLATE_LAYOUT_KEYS]).toEqual([
      "navMode",
      "navShape",
      "card",
      "pattern",
      "fontHeading",
      "size",
      "scale",
      "lineHeight",
      "tracking",
      "width",
    ]);
  });

  it("keeps Klassik when only layout chrome differs (APP-8 rejected)", () => {
    const dirty: AppearancePrefs = { ...classicPage, ...layout };
    expect(matchTemplate(dirty, a11y, "system")?.id).toBe("classic");
  });

  it("preserves layout chrome when a team template is applied", () => {
    const classic = TEMPLATES.find((row) => row.id === "classic");
    expect(classic).toBeTruthy();
    const next = templateAppearance(classic!, { style: "clay", ...layout });
    for (const key of TEMPLATE_LAYOUT_KEYS) {
      expect(next[key]).toBe(layout[key]);
    }
    expect(matchTemplate({ ...next }, a11y, "system")?.id).toBe("classic");
  });
});
