import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  CHECK_SHAPES,
  CONFIRM_KINDS,
  COPY_TONES,
  TAB_TONES,
  TIME_TONES,
  TIP_KINDS,
  clampTipKind,
} from "@/lib/theme/kit";

describe("kit catalogs", () => {
  it("keeps the selected confirm set", () => {
    expect(CONFIRM_KINDS).toEqual([
      "modal",
      "popover",
      "inline",
      "hold",
      "cmdk",
    ]);
  });

  it("ships every tooltip tone", () => {
    expect(TIP_KINDS).toHaveLength(10);
    expect(clampTipKind("soft")).toBe("soft");
    expect(clampTipKind("nope")).toBe("balloon");
  });

  it("omits the 44px check variant", () => {
    expect(CHECK_SHAPES).not.toContain("big");
    expect(CHECK_SHAPES).toHaveLength(9);
  });

  it("omits token-burn copy", () => {
    expect(COPY_TONES).not.toContain("burn");
    expect(COPY_TONES).toHaveLength(8);
  });

  it("keeps ten time and tab tones", () => {
    expect(TIME_TONES).toHaveLength(10);
    expect(TAB_TONES).toHaveLength(10);
  });
});

describe("kit CSS", () => {
  const css = readFileSync(
    fileURLToPath(new URL("../../src/app/kit.css", import.meta.url)),
    "utf8",
  );

  it("ships the chosen chrome", () => {
    expect(css).toContain('[data-kit-tip="balloon"]');
    expect(css).toContain('[data-kit-confirm="cmdk"]');
    expect(css).toContain('[data-kit-copy="ghost"]');
    expect(css).toContain('[data-kit-tabs="vertical"]');
    expect(css).toContain('[data-kit-check="switch"]');
    expect(css).toContain(".rw-kit-hold");
    expect(css).toContain(".rw-kit-toast");
    expect(css).toContain('[data-kit-tip="flip"]');
    expect(css).toContain('[data-kit-tabs="badge"]');
    expect(css).toContain('[data-kit-tabs="scroll"]');
  });
});

describe("kit product surfaces", () => {
  const src = (rel: string) =>
    readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf8");

  it("wires the selected confirm kinds", () => {
    expect(src("../../src/components/admin/CrudPage.tsx")).toContain(
      'kind: "popover"',
    );
    expect(src("../../src/components/settings/TeamsSection.tsx")).toContain(
      "InlineConfirm",
    );
    expect(src("../../src/components/admin/ArenaAdmin.tsx")).toContain(
      'kind: "hold"',
    );
    expect(src("../../src/components/admin/UsersAdmin.tsx")).toContain(
      'kind: "cmdk"',
    );
  });

  it("wires tooltip, copy, time, tab, and check surfaces", () => {
    expect(src("../../src/layout/AppHeader.tsx")).toContain(
      'data-tip-kind="flip"',
    );
    expect(src("../../src/components/settings/NotificationsSection.tsx")).toContain(
      "InfoMark",
    );
    expect(src("../../src/components/profile/ActivityHeatmap.tsx")).toContain(
      'data-tip-kind="legend"',
    );
    expect(src("../../src/app/problems/[slug]/page.tsx")).toContain(
      'tone="hover"',
    );
    expect(src("../../src/app/contests/[slug]/page.tsx")).toContain(
      'tone="dual"',
    );
    expect(src("../../src/components/profile/ProfileNav.tsx")).toContain(
      'data-kit-tabs="scroll"',
    );
    expect(src("../../src/components/profile/ProblemMap.tsx")).toContain(
      'tone="badge"',
    );
    expect(src("../../src/components/customizer/Customizer.tsx")).toContain(
      "FormStepper",
    );
  });
});
