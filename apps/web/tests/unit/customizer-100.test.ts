import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const customizer = src("../../src/components/customizer/Customizer.tsx");
const appearance = src("../../src/components/customizer/AppearanceTab.tsx");
const settings = src("../../src/components/settings/AppearanceSection.tsx");
const search = src("../../src/layout/SearchBox.tsx");
const overlay = src("../../src/components/overlay/OverlayHost.tsx");
const chrome = src("../../src/components/customizer/chrome.ts");

describe("CUST-100 contestant customizer", () => {
  it("is a tablist with two panels, not a kit playground", () => {
    expect(customizer).toContain('role="tablist"');
    expect(customizer).toContain('role="tab"');
    expect(customizer).toContain("<AppearanceTab");
    expect(customizer).toContain("<A11yTab");
    expect(customizer).not.toContain("KitSection");
    expect(customizer).not.toContain("IconGallery");
    expect(customizer).not.toContain("FormIconSwitch");
    expect(appearance).not.toContain("FormIconSwitch");
    expect(appearance).not.toContain("KitSection");
    expect(appearance).not.toContain("IconGallery");
  });

  it("groups appearance into four accordion clusters", () => {
    expect(chrome).toContain('"look"');
    expect(chrome).toContain('"color"');
    expect(chrome).toContain('"type"');
    expect(chrome).toContain('"system"');
    expect(appearance).toContain('id="look"');
    expect(appearance).toContain('id="color"');
    expect(appearance).toContain('id="type"');
    expect(appearance).toContain('id="system"');
    expect(src("../../src/components/customizer/Group.tsx")).toContain(
      "aria-expanded",
    );
  });

  it("labels swatches and overlay samples; demos skip the tab order", () => {
    expect(chrome).toContain("customizer.swatch.blue");
    expect(appearance).toContain("overlay.sample.popover");
    expect(appearance).toContain("overlay.sample.hold");
    expect(appearance).toContain("overlay.sample.cmdk");
    expect(appearance).toMatch(/inert/);
    expect(appearance).toContain("tabIndex={-1}");
  });

  it("imports a file without a native empty-state label", () => {
    const saved = src("../../src/components/customizer/SavedTemplates.tsx");
    expect(saved).toContain("customizer.importFile");
    expect(saved).toContain('type="file"');
    expect(saved).toContain("sr-only");
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
});
