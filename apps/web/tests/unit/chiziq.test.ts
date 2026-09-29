import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  CHIZIQ_TICK,
  axisOverflows,
  intersectBoxes,
  shrinkPageClip,
  tickOffset,
  tickSize,
  viewportOverflows,
} from "@/lib/chiziq";

describe("tickSize", () => {
  it("keeps the preferred tick on a long track", () => {
    expect(tickSize(200)).toBe(CHIZIQ_TICK);
  });

  it("shrinks to the track when the pane is shorter than the tick", () => {
    expect(tickSize(14)).toBe(14);
    expect(tickSize(0)).toBe(0);
  });
});

describe("tickOffset", () => {
  it("sits at the start when scroll is 0", () => {
    expect(tickOffset(0, 400, 200)).toBe(0);
  });

  it("sits at the end when scrolled to the max", () => {
    expect(tickOffset(400, 400, 200)).toBe(200 - CHIZIQ_TICK);
  });

  it("scales linearly in the middle", () => {
    expect(tickOffset(200, 400, 200)).toBe((200 - CHIZIQ_TICK) / 2);
  });

  it("does not run past the track", () => {
    expect(tickOffset(999, 400, 200)).toBe(200 - CHIZIQ_TICK);
    expect(tickOffset(-20, 400, 200)).toBe(0);
  });
});

describe("axisOverflows", () => {
  it("requires overflow auto/scroll and extra content", () => {
    expect(
      axisOverflows({
        overflowX: "auto",
        overflowY: "hidden",
        scrollWidth: 900,
        scrollHeight: 900,
        clientWidth: 300,
        clientHeight: 300,
      }),
    ).toEqual({ x: true, y: false });
  });

  it("ignores visible overflow even when content is larger", () => {
    expect(
      axisOverflows({
        overflowX: "visible",
        overflowY: "visible",
        scrollWidth: 900,
        scrollHeight: 900,
        clientWidth: 300,
        clientHeight: 300,
      }),
    ).toEqual({ x: false, y: false });
  });
});

describe("viewportOverflows", () => {
  it("does not look at CSS overflow — the document still scrolls", () => {
    expect(
      viewportOverflows({
        scrollWidth: 400,
        scrollHeight: 2000,
        clientWidth: 400,
        clientHeight: 800,
      }),
    ).toEqual({ x: false, y: true });
  });
});

describe("intersectBoxes", () => {
  it("returns the overlap", () => {
    expect(
      intersectBoxes(
        { top: 0, left: 0, right: 100, bottom: 100, width: 100, height: 100 },
        { top: 50, left: 50, right: 150, bottom: 150, width: 100, height: 100 },
      ),
    ).toEqual({ top: 50, left: 50, right: 100, bottom: 100, width: 50, height: 50 });
  });

  it("drops boxes that are too small to host a tick", () => {
    expect(
      intersectBoxes(
        { top: 0, left: 0, right: 10, bottom: 10, width: 10, height: 10 },
        { top: 8, left: 8, right: 12, bottom: 12, width: 4, height: 4 },
      ),
    ).toBeNull();
  });
});

describe("shrinkPageClip", () => {
  const page = {
    top: 0,
    left: 0,
    right: 1000,
    bottom: 800,
    width: 1000,
    height: 800,
  };
  const viewport = { width: 1000, height: 800 };

  it("moves the page rail left of a right-edge overlay", () => {
    expect(
      shrinkPageClip(
        page,
        { top: 0, left: 700, right: 1000, bottom: 800, width: 300, height: 800 },
        viewport,
      ),
    ).toEqual({ top: 0, left: 0, right: 700, bottom: 800, width: 700, height: 800 });
  });

  it("ignores a left sidebar that does not cover the viewport edge", () => {
    expect(
      shrinkPageClip(
        page,
        { top: 0, left: 0, right: 260, bottom: 800, width: 260, height: 800 },
        viewport,
      ),
    ).toEqual(page);
  });
});

describe("theme.css Chiziq wiring", () => {
  const css = readFileSync(
    fileURLToPath(new URL("../../src/app/theme.css", import.meta.url)),
    "utf8",
  );

  it("hides the native scrollbar globally", () => {
    expect(css).toContain("scrollbar-width: none !important");
    expect(css).toContain("*::-webkit-scrollbar");
  });

  it("draws the 2px rail and the red tick token", () => {
    expect(css).toContain(".rw-chiziq-y");
    expect(css).toContain("width: 2px");
    expect(css).toContain("var(--rw-bad-ink)");
  });

  it("does not keep the old 6px gray table thumb", () => {
    expect(css).not.toMatch(/custom-scrollbar[\s\S]*bg-gray-200/);
  });
});
