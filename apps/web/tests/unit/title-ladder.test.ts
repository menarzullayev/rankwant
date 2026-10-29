import { beforeAll, describe, expect, it } from "vitest";

import { en } from "@/i18n/locales/en";
import { registerMessages } from "@/i18n/messages";

import { TITLE_ICON_CODES } from "@/components/ui/Identity/TitleIcon";
import { TITLE_BLOCKS, TITLE_LADDER, nextTier, titleTooltip } from "@/lib/title-ladder";

beforeAll(() => {
  registerMessages("en", en);
});

describe("title ladder", () => {
  it("has 16 tiers, strictly ascending", () => {
    expect(TITLE_LADDER).toHaveLength(16);
    TITLE_LADDER.forEach((tier, i) => {
      expect(tier.level).toBe(i + 1);
      if (i > 0) expect(tier.min).toBeGreaterThan(TITLE_LADDER[i - 1].min);
    });
  });

  it("draws an icon for every tier and nothing else", () => {
    expect(TITLE_ICON_CODES).toEqual(TITLE_LADDER.map((tier) => tier.code));
  });

  it("keeps each block contiguous and in ladder order", () => {
    const seen = TITLE_LADDER.map((tier) => tier.block).filter((b, i, all) => all.indexOf(b) === i);
    expect(seen).toEqual(TITLE_BLOCKS);
  });

  it("knows the tier above, and that the top has none", () => {
    expect(nextTier("comet")?.code).toBe("moon");
    expect(nextTier("cosmos")).toBeUndefined();
  });

  it("writes the tooltip with the next tier and its bound", () => {
    expect(titleTooltip("en", "comet")).toBe("Comet · tier 6 of 16 · next: Moon from 1500");
    expect(titleTooltip("en", "cosmos")).toBe("Cosmos · tier 16 of 16 · highest tier");
  });
});
