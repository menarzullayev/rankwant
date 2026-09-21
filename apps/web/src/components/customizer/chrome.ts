import type { MessageKey } from "@/i18n/messages";

/** Shared chrome for the contestant customizer — not the kit lab. */

/** D61: layout chrome and kit families unmount separately. */
export const GROUPS = ["look", "color", "type", "layout", "system"] as const;
export type GroupId = (typeof GROUPS)[number];

/** D48: contestant Interfeys writes these. `/admin/kit` is sample-only. */
export const KIT_FAMILY_KEYS = [
  "verdictStyle",
  "statusStyle",
  "loadingStyle",
  "overlayStyle",
  "formStyle",
  "iconPack",
] as const;
export type KitFamilyKey = (typeof KIT_FAMILY_KEYS)[number];

/** D53: Interfeys layout families stay chips (2–5 options). Kit is SelectField. */
export const LAYOUT_CHIP_KEYS = ["navMode", "navShape", "card", "pattern"] as const;

export const DENSITIES = ["compact", "comfortable", "spacious"] as const;

export const SWATCHES: { hue: number; sat: number; nameKey: MessageKey }[] = [
  { hue: 0, sat: 70, nameKey: "customizer.swatch.red" },
  { hue: 20, sat: 80, nameKey: "customizer.swatch.ember" },
  { hue: 38, sat: 85, nameKey: "customizer.swatch.orange" },
  { hue: 52, sat: 70, nameKey: "customizer.swatch.yellow" },
  { hue: 95, sat: 55, nameKey: "customizer.swatch.lime" },
  { hue: 140, sat: 55, nameKey: "customizer.swatch.green" },
  { hue: 170, sat: 60, nameKey: "customizer.swatch.teal" },
  { hue: 195, sat: 70, nameKey: "customizer.swatch.cyan" },
  { hue: 215, sat: 75, nameKey: "customizer.swatch.blue" },
  { hue: 240, sat: 65, nameKey: "customizer.swatch.indigo" },
  { hue: 262, sat: 70, nameKey: "customizer.swatch.violet" },
  { hue: 290, sat: 60, nameKey: "customizer.swatch.magenta" },
  { hue: 320, sat: 65, nameKey: "customizer.swatch.pink" },
  { hue: 345, sat: 70, nameKey: "customizer.swatch.rose" },
];

export const chip = (active: boolean) =>
  `rw-radius-sm border px-3 py-1.5 text-theme-sm transition rw-focus-ring ${
    active ? "rw-accent-line rw-accent-soft" : "rw-line rw-dim-2 rw-hover-bg"
  }`;
