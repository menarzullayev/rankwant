import { fill, t, type Locale } from "@/i18n/messages";

/** The 16-tier contest ladder as the web needs it (ADR-0027).
 *
 *  Mirrors `TITLES` in apps/api/profiles/titles.py: lower bound and code.
 *  `block` is the ladder grouping shown to the user (Matter … Everything);
 *  it exists only here. `tools/check_decisions.py` →
 *  `title_ladder_matches_the_api` keeps both lists equal. */
export type TitleBlock = "matter" | "cosmicBody" | "stellar" | "extreme" | "structure" | "everything";

export type TitleTier = { code: string; level: number; min: number; block: TitleBlock };

const ROWS: [string, number, TitleBlock][] = [
  ["quark", 0, "matter"],
  ["atom", 600, "matter"],
  ["molecule", 900, "matter"],
  ["droplet", 1200, "matter"],
  ["meteorite", 1300, "cosmicBody"],
  ["comet", 1400, "cosmicBody"],
  ["moon", 1500, "cosmicBody"],
  ["planet", 1600, "cosmicBody"],
  ["star", 1900, "stellar"],
  ["supernova", 2100, "stellar"],
  ["pulsar", 2300, "extreme"],
  ["magnetar", 2400, "extreme"],
  ["black_hole", 2600, "extreme"],
  ["galaxy", 3000, "structure"],
  ["supercluster", 3200, "structure"],
  ["cosmos", 3500, "everything"],
];

export const TITLE_LADDER: TitleTier[] = ROWS.map(([code, min, block], i) => ({
  code,
  level: i + 1,
  min,
  block,
}));

export const TITLE_BLOCKS: TitleBlock[] = ["matter", "cosmicBody", "stellar", "extreme", "structure", "everything"];

export const tierOf = (code: string): TitleTier | undefined =>
  TITLE_LADDER.find((tier) => tier.code === code);

export const nextTier = (code: string): TitleTier | undefined => {
  const tier = tierOf(code);
  return tier ? TITLE_LADDER[tier.level] : undefined;
};

/** `Comet · tier 6 of 16 · next: Moon from 1500` — the hover text on a title. */
export function titleTooltip(locale: Locale, code: string): string {
  const tier = tierOf(code);
  const name = t(locale, `title.${code}`);
  if (!tier) return name;
  const next = nextTier(code);
  const params = { name, level: tier.level, total: TITLE_LADDER.length };
  return next
    ? fill(t(locale, "title.tooltip"), {
        ...params,
        next: t(locale, `title.${next.code}`),
        min: next.min,
      })
    : fill(t(locale, "title.tooltipTop"), params);
}
