/** Header mavzu tugmasi uslublari (H6). Owner tanlovi: 01 02 03 04 07 08 10.
 *  Standart — `doira` (prototip 03, ThemeContext circle). */

import type { ThemeEffect } from "@/lib/api";

export const THEME_TOGGLES = [
  "aylanma",
  "relss",
  "doira",
  "ufq",
  "morph",
  "osmon",
  "parda",
] as const;

export type ThemeToggleId = (typeof THEME_TOGGLES)[number];

/** Prototip 03 — mahsulotdagi circle View Transition. */
export const DEFAULT_THEME_TOGGLE: ThemeToggleId = "doira";

export const isThemeToggle = (value: unknown): value is ThemeToggleId =>
  typeof value === "string" &&
  (THEME_TOGGLES as readonly string[]).includes(value);

export function clampThemeToggle(value: unknown): ThemeToggleId {
  return isThemeToggle(value) ? value : DEFAULT_THEME_TOGGLE;
}

/** Tugma uslubi → sahifa View Transition. */
export function themeToggleToEffect(id: ThemeToggleId): ThemeEffect {
  if (id === "doira") return "circle";
  if (id === "parda") return "curtain";
  return "fade";
}
