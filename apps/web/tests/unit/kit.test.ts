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
    expect(css).toContain(".rw-kit-hold-hint");
    expect(css).toContain(".rw-kit-hold-track");
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
    expect(src("../../src/features/account/components/AccountSettings.tsx")).toContain(
      'kind: "modal"',
    );
    expect(src("../../src/components/admin/CrudPage.tsx")).toContain(
      'kind: "popover"',
    );
    expect(src("../../src/features/account/components/TeamsSection.tsx")).toContain(
      "InlineConfirm",
    );
    expect(src("../../src/components/admin/ArenaAdmin.tsx")).toContain(
      'kind: "hold"',
    );
    expect(src("../../src/components/kit/ConfirmExtras.tsx")).toContain(
      "kit.holdHint",
    );
    expect(src("../../src/components/kit/ConfirmExtras.tsx")).toContain(
      "rw-kit-hold-hint",
    );
    expect(src("../../src/components/admin/UsersAdmin.tsx")).toContain(
      'kind: "cmdk"',
    );
    expect(src("../../src/layout/AppShell.tsx")).not.toContain(
      "<CommandPalette",
    );
  });

  it("wires tooltip, copy, time, tab, and check surfaces", () => {
    expect(src("../../src/layout/AppHeader.tsx")).toContain(
      'data-tip-kind="flip"',
    );
    expect(src("../../src/components/ui/Verdict.tsx")).toContain(
      'data-tip-kind="soft"',
    );
    expect(src("../../src/features/profile/components/ProblemMap.tsx")).toContain(
      'data-tip-kind="rich"',
    );
    expect(src("../../src/features/account/components/NotificationsSection.tsx")).toContain(
      "InfoMark",
    );
    expect(src("../../src/components/customizer/CustomizerTrigger.tsx")).toContain(
      'data-tip-kind="kbd"',
    );
    expect(src("../../src/features/profile/components/RatingChart.tsx")).toContain(
      'data-tip-kind="follow"',
    );
    expect(src("../../src/features/profile/components/ActivityHeatmap.tsx")).toContain(
      'data-tip-kind="legend"',
    );
    expect(src("../../src/features/profile/components/ActivityHeatmap.tsx")).toContain(
      "SKELETON_TIP",
    );
    expect(src("../../src/components/kit/TimeStamp.tsx")).toContain(
      'data-tip-kind="theme"',
    );
    expect(src("../../src/app/(site)/problems/[slug]/page.tsx")).toContain(
      'tone="hover"',
    );
    expect(src("../../src/features/problems/components/SampleTests.tsx")).toContain(
      'tone="ghost"',
    );
    expect(src("../../src/features/problems/components/Editorial.tsx")).toContain("CodeCopy");
    expect(src("../../src/features/account/components/TeamsSection.tsx")).toContain(
      'tone="chip"',
    );
    expect(src("../../src/components/admin/CrudPage.tsx")).toContain("CopyCell");
    expect(src("../../src/features/contests/components/StandingsTable.tsx")).toContain(
      "CopyAllBar",
    );
    expect(src("../../src/features/problems/components/SubmitPanel.tsx")).toContain('tone="kbd"');
    expect(src("../../src/components/kit/CopyControl.tsx")).toContain(
      "overlay.toast",
    );
    expect(src("../../src/components/kit/CopyControl.tsx")).toContain(
      "problem.copyFailed",
    );
    expect(src("../../src/components/kit/CommandPalette.tsx")).toContain(
      "problem.copyFailed",
    );
    expect(src("../../src/features/profile/components/ShareButton.tsx")).toContain(
      "problem.copyFailed",
    );
    expect(src("../../src/app/(site)/contests/[slug]/page.tsx")).toContain(
      'tone="dual"',
    );
    expect(src("../../src/app/(site)/contests/[slug]/page.tsx")).toContain("Countdown");
    expect(src("../../src/features/profile/components/ProfileCard.tsx")).toContain(
      'tone="relative"',
    );
    expect(src("../../src/features/profile/components/ProfileCard.tsx")).toContain(
      'tone="locale"',
    );
    expect(src("../../src/features/profile/components/ActivityTabs.tsx")).toContain(
      'tone="badge"',
    );
    expect(src("../../src/features/submissions/components/AttemptView.tsx")).toContain("TimeLine");
    expect(src("../../src/features/profile/components/AttemptsTab.tsx")).toContain(
      'tone="iso"',
    );
    expect(src("../../src/features/profile/components/ContestsTab.tsx")).toContain(
      'tone="duration"',
    );
    expect(src("../../src/app/(site)/calendar/page.tsx")).toContain('tone="fresh"');
    expect(src("../../src/features/profile/components/ActivityHeatmap.tsx")).toContain(
      "MiniCal",
    );
    expect(src("../../src/features/profile/components/ProfileNav.tsx")).toContain(
      'data-kit-tabs="scroll"',
    );
    expect(src("../../src/features/profile/components/ProblemMap.tsx")).toContain(
      'tone="badge"',
    );
    expect(src("../../src/features/profile/components/ProblemMap.tsx")).toContain(
      'data-kit-tabs="icon"',
    );
    expect(src("../../src/features/problems/components/ProblemTabs.tsx")).toContain(
      'data-kit-tabs="underline"',
    );
    expect(src("../../src/features/auth/components/AuthTabs.tsx")).toContain(
      'data-kit-tabs="segment"',
    );
    expect(src("../../src/features/profile/components/RatingChart.tsx")).toContain(
      'data-kit-tabs="card"',
    );
    expect(src("../../src/features/problems/components/ProblemFilters.tsx")).toContain(
      'data-kit-tabs="chips"',
    );
    expect(src("../../src/features/account/components/OnboardingForm.tsx")).toContain(
      'tone="step"',
    );
    expect(src("../../src/features/account/components/SettingsShell.tsx")).toContain(
      'data-kit-tabs="crumb"',
    );
    expect(src("../../src/features/account/components/SettingsShell.tsx")).toContain(
      'data-kit-tabs="vertical"',
    );
    expect(src("../../src/components/customizer/AppearanceTab.tsx")).toContain(
      "FormStepper",
    );
    expect(src("../../src/components/customizer/AppearanceTab.tsx")).toContain(
      "FormSeg3",
    );
    expect(src("../../src/components/kit/KitPlayground.tsx")).toContain(
      "FormIconSwitch",
    );
    expect(src("../../src/components/kit/KitPlayground.tsx")).toContain(
      'shape="card"',
    );
    expect(src("../../src/components/admin/CrudPage.tsx")).toContain(
      'shape="pill"',
    );
    expect(src("../../src/features/account/components/NotificationsSection.tsx")).toContain(
      'shape="switch"',
    );
    expect(src("../../src/features/problems/components/ProblemFilters.tsx")).toContain(
      "FormTreeItem",
    );
    expect(src("../../src/features/account/components/AppearanceSection.tsx")).toContain(
      'tone="card"',
    );
    expect(src("../../src/components/form/FormKit.tsx")).toContain(
      'data-kit-check={tone === "card" ? "radio-card" : undefined}',
    );
  });
});
