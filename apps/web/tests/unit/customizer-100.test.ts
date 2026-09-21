import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { Group } from "@/components/customizer/Group";
import { KIT_FAMILY_KEYS, LAYOUT_CHIP_KEYS } from "@/components/customizer/chrome";
import { clampGroup, DEFAULT_GROUP, GROUP_SESSION_KEY } from "@/components/customizer/group-session";
import { clampTab, DEFAULT_TAB, TAB_SESSION_KEY } from "@/components/customizer/tab-session";
import { nextTab } from "@/components/customizer/tabs";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const customizer = src("../../src/components/customizer/Customizer.tsx");
const appearance = src("../../src/components/customizer/AppearanceTab.tsx");
const settings = src("../../src/components/settings/AppearanceSection.tsx");
const search = src("../../src/layout/SearchBox.tsx");
const overlay = src("../../src/components/overlay/OverlayHost.tsx");
const chrome = src("../../src/components/customizer/chrome.ts");
const saved = src("../../src/components/customizer/SavedTemplates.tsx");
const groupSession = src("../../src/components/customizer/group-session.ts");
const tabSession = src("../../src/components/customizer/tab-session.ts");

describe("CUST-100 contestant customizer", () => {
  it("is a keyboard tablist with two panels, not a kit playground", () => {
    expect(customizer).toContain('role="tablist"');
    expect(customizer).toContain("nextTab");
    expect(customizer).toContain("aria-orientation");
    expect(customizer).toContain("<AppearanceTab");
    expect(customizer).toContain("<A11yTab");
    expect(customizer).toContain("D60");
    expect(customizer).toContain("D64");
    expect(customizer).not.toContain('from "next/dynamic"');
    expect(customizer).not.toContain("lazy(() =>");
    expect(customizer).toContain('import { AppearanceTab } from "./AppearanceTab"');
    expect(customizer).toContain('import { A11yTab } from "./A11yTab"');
    expect(appearance).not.toContain("<A11yTab");
    expect(customizer).not.toContain("KitSection");
    expect(customizer).not.toContain("IconGallery");
    expect(customizer).not.toContain("FormIconSwitch");
    expect(appearance).not.toContain("FormIconSwitch");
    expect(appearance).not.toContain("KitSection");
    expect(appearance).not.toContain("IconGallery");
    expect(appearance).not.toContain("FormFile");
    expect(appearance).not.toContain("overlay.sample.popover");
  });

  it("moves the tab selection with arrows, Home, and End", () => {
    expect(nextTab("appearance", "ArrowRight")).toBe("a11y");
    expect(nextTab("a11y", "ArrowRight")).toBe("appearance");
    expect(nextTab("a11y", "ArrowLeft")).toBe("appearance");
    expect(nextTab("appearance", "Home")).toBe("appearance");
    expect(nextTab("a11y", "Home")).toBe("appearance");
    expect(nextTab("appearance", "End")).toBe("a11y");
    expect(nextTab("appearance", "Enter")).toBeNull();
  });

  it("unmounts a closed accordion group so its controls leave the tab order", () => {
    const probe = createElement("button", { type: "button" }, "inside-control");
    const closed = renderToStaticMarkup(
      createElement(
        Group,
        { id: "look", title: "Look", open: false, onOpen() {} },
        probe,
      ),
    );
    expect(closed).not.toContain("inside-control");
    expect(closed).toContain('aria-expanded="false"');

    const opened = renderToStaticMarkup(
      createElement(
        Group,
        { id: "look", title: "Look", open: true, onOpen() {} },
        probe,
      ),
    );
    expect(opened).toContain("inside-control");
    expect(opened).toContain('aria-expanded="true"');
    expect(opened).toContain('id="rw-cz-look"');
  });

  it("groups appearance into five accordion clusters (D61)", () => {
    expect(chrome).toContain('"look"');
    expect(chrome).toContain('"color"');
    expect(chrome).toContain('"type"');
    expect(chrome).toContain('"layout"');
    expect(chrome).toContain('"system"');
    expect(appearance).toContain('id="look"');
    expect(appearance).toContain('id="color"');
    expect(appearance).toContain('id="type"');
    expect(appearance).toContain('id="layout"');
    expect(appearance).toContain('id="system"');
    const layoutAt = appearance.indexOf('id="layout"');
    const systemAt = appearance.indexOf('id="system"');
    expect(layoutAt).toBeGreaterThan(-1);
    expect(systemAt).toBeGreaterThan(layoutAt);
    expect(appearance.indexOf("<NavSection")).toBeGreaterThan(layoutAt);
    expect(appearance.indexOf("<NavSection")).toBeLessThan(systemAt);
    expect(appearance.indexOf("<LookSection")).toBeGreaterThan(layoutAt);
    expect(appearance.indexOf("<LookSection")).toBeLessThan(systemAt);
    expect(appearance.indexOf("<VerdictSection")).toBeGreaterThan(systemAt);
    expect(appearance.indexOf("<IconPackSection")).toBeGreaterThan(systemAt);
    expect(appearance).toContain("D61");
  });

  it("labels swatches; demos that stay in the panel skip the tab order", () => {
    expect(chrome).toContain("customizer.swatch.blue");
    expect(appearance).toMatch(/inert/);
    expect(src("../../src/components/kit/KitPlayground.tsx")).toContain(
      "overlay.sample.popover",
    );
    expect(src("../../src/components/kit/KitPlayground.tsx")).toContain(
      "overlay.sample.hold",
    );
    expect(src("../../src/components/kit/KitPlayground.tsx")).toContain(
      "overlay.sample.cmdk",
    );
  });

  it("imports a file without a native empty-state label", () => {
    expect(saved).toContain("customizer.importFile");
    expect(saved).toContain('type="file"');
    expect(saved).toContain("sr-only");
    expect(saved).toContain("tabIndex={-1}");
    expect(saved).toContain('aria-hidden="true"');
    expect(saved).not.toContain("FormFile");
    expect(saved).toContain("customizer.deleteConfirm");
  });

  it("closes the settings theme/style duplicate", () => {
    expect(settings).toContain("settings.openCustomizer");
    expect(settings).toContain("setOpen(true)");
    expect(settings).not.toContain("STYLES.map");
    expect(settings).not.toContain("setMode");
    expect(settings).not.toContain("setStyle");
  });

  it("keeps the header search from covering the palette", () => {
    expect(search).toContain("w-full max-w-full");
    expect(search).not.toMatch(/w-64/);
    expect(overlay).toContain('pointerdown"');
    expect(src("../../src/app/(site)/admin/kit/page.tsx")).toContain("KitSection");
    expect(src("../../src/components/admin/sections.ts")).toContain("/admin/kit");
  });

  it("lets the contestant Interfeys write kit families; the lab does not (D48)", () => {
    expect(KIT_FAMILY_KEYS).toEqual([
      "verdictStyle",
      "statusStyle",
      "loadingStyle",
      "overlayStyle",
      "formStyle",
      "iconPack",
    ]);
    expect(chrome).toContain("KIT_FAMILY_KEYS");
    for (const key of KIT_FAMILY_KEYS) {
      expect(appearance).toContain(`setAppearance({ ${key}:`);
    }
    expect(appearance).toContain("D48");
    const kitPage = src("../../src/app/(site)/admin/kit/page.tsx");
    const playground = src("../../src/components/kit/KitPlayground.tsx");
    expect(kitPage).not.toContain("setAppearance");
    expect(playground).not.toContain("setAppearance");
    expect(playground).not.toContain("useCustomizer");
    expect(customizer).not.toContain("KitFamilyTab");
  });

  it("uses six labeled SelectFields for kit families, not a chip wall (D51)", () => {
    expect((appearance.match(/<SelectField/g) || []).length).toBe(6);
    expect(appearance).not.toContain("onClick={() => setAppearance({ verdictStyle");
    expect(appearance).not.toContain("onClick={() => setAppearance({ statusStyle");
    expect(appearance).not.toContain("onClick={() => setAppearance({ loadingStyle");
    expect(appearance).not.toContain("onClick={() => setAppearance({ overlayStyle");
    expect(appearance).not.toContain("onClick={() => setAppearance({ formStyle");
    expect(appearance).not.toContain("onClick={() => setAppearance({ iconPack");
  });

  it("keeps layout families as chips, not SelectFields (D53)", () => {
    expect([...LAYOUT_CHIP_KEYS]).toEqual(["navMode", "navShape", "card", "pattern"]);
    for (const key of LAYOUT_CHIP_KEYS) {
      expect(appearance).toContain(`setAppearance({ ${key}:`);
      expect(appearance).toContain(`onClick={() => setAppearance({ ${key}:`);
    }
    expect(appearance).toContain("D53");
    expect((appearance.match(/<SelectField/g) || []).length).toBe(6);
  });

  it("keeps content width as a slider only (D58)", () => {
    expect(appearance).toContain("D58");
    expect(appearance).toContain("type=\"range\"");
    expect(appearance).not.toContain("WIDTH_STEPS");
    expect(appearance).not.toContain("setAppearance({ width: preset })");
  });

  it("keeps four Type size snap chips (D59)", () => {
    expect(appearance).toContain("D59");
    expect(appearance).toContain("const quick = [90, 100, 110, 120]");
    expect(appearance).toContain("setAppearance({ size: preset })");
  });

  it("remembers the last accordion in sessionStorage (D65)", () => {
    expect(appearance).toContain("D65");
    expect(appearance).toContain("writeGroup");
    expect(groupSession).toContain("sessionStorage.setItem");
    expect(groupSession).not.toMatch(/localStorage\.(get|set)Item/);
    expect(GROUP_SESSION_KEY).toBe("rw:cz-group");
    expect(clampGroup("system")).toBe("system");
    expect(clampGroup("layout")).toBe("layout");
    expect(clampGroup("nope")).toBe(DEFAULT_GROUP);
  });

  it("remembers the last panel tab in sessionStorage (D66)", () => {
    expect(customizer).toContain("D66");
    expect(customizer).toContain("writeTab");
    expect(customizer).not.toContain("useState");
    expect(tabSession).toContain("sessionStorage.setItem");
    expect(tabSession).not.toMatch(/localStorage\.(get|set)Item/);
    expect(TAB_SESSION_KEY).toBe("rw:cz-tab");
    expect(clampTab("a11y")).toBe("a11y");
    expect(clampTab("appearance")).toBe("appearance");
    expect(clampTab("nope")).toBe(DEFAULT_TAB);
  });
});
