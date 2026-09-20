import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { Group } from "@/components/customizer/Group";
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

describe("CUST-100 contestant customizer", () => {
  it("is a keyboard tablist with two panels, not a kit playground", () => {
    expect(customizer).toContain('role="tablist"');
    expect(customizer).toContain("nextTab");
    expect(customizer).toContain("aria-orientation");
    expect(customizer).toContain("<AppearanceTab");
    expect(customizer).toContain("<A11yTab");
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

  it("groups appearance into four accordion clusters", () => {
    expect(chrome).toContain('"look"');
    expect(chrome).toContain('"color"');
    expect(chrome).toContain('"type"');
    expect(chrome).toContain('"system"');
    expect(appearance).toContain('id="look"');
    expect(appearance).toContain('id="color"');
    expect(appearance).toContain('id="type"');
    expect(appearance).toContain('id="system"');
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
