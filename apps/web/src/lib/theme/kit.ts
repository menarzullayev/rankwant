/** Situational interaction kit — tanlangan variantlar.
 *
 * Overlay/form oilalaridan farq: bu yerda foydalanuvchi 10 ta chip
 * tanlamaydi. Har bir sath o'z qoidasiga bo'ysunadi (o'chirish qatori —
 * popover, ommaviy amal — hold, admin kuchi — command palette).
 * Ko'rinish hali ham `data-overlay` / `data-form` tokenlaridan keladi.
 */

export type ConfirmKind = "modal" | "popover" | "inline" | "hold" | "cmdk";

export type TipKind =
  | "balloon"
  | "soft"
  | "rich"
  | "info"
  | "kbd"
  | "flip"
  | "follow"
  | "legend"
  | "skeleton"
  | "theme";

export type CheckShape =
  | "square"
  | "pill"
  | "card"
  | "switch"
  | "icon"
  | "stepper"
  | "tree"
  | "radio-card"
  | "seg3";

export type TimeTone =
  | "relative"
  | "dual"
  | "badge"
  | "timeline"
  | "countdown"
  | "duration"
  | "iso"
  | "fresh"
  | "locale"
  | "cal";

export type CopyTone =
  | "text"
  | "ghost"
  | "code"
  | "chip"
  | "hover"
  | "cell"
  | "all"
  | "kbd";

export type TabTone =
  | "underline"
  | "segment"
  | "card"
  | "icon"
  | "badge"
  | "chips"
  | "step"
  | "scroll"
  | "crumb"
  | "vertical";

export const CONFIRM_KINDS: ConfirmKind[] = [
  "modal",
  "popover",
  "inline",
  "hold",
  "cmdk",
];

export const TIP_KINDS: TipKind[] = [
  "balloon",
  "soft",
  "rich",
  "info",
  "kbd",
  "flip",
  "follow",
  "legend",
  "skeleton",
  "theme",
];

export const CHECK_SHAPES: CheckShape[] = [
  "square",
  "pill",
  "card",
  "switch",
  "icon",
  "seg3",
  "radio-card",
  "tree",
  "stepper",
];

export const TIME_TONES: TimeTone[] = [
  "relative",
  "dual",
  "badge",
  "timeline",
  "countdown",
  "cal",
  "locale",
  "fresh",
  "iso",
  "duration",
];

export const COPY_TONES: CopyTone[] = [
  "text",
  "ghost",
  "code",
  "chip",
  "hover",
  "cell",
  "all",
  "kbd",
];

export const TAB_TONES: TabTone[] = [
  "underline",
  "segment",
  "card",
  "icon",
  "badge",
  "chips",
  "step",
  "scroll",
  "crumb",
  "vertical",
];

export function clampTipKind(value: string | null): TipKind {
  if (TIP_KINDS.includes(value as TipKind)) return value as TipKind;
  return "balloon";
}
