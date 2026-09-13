/** Sozlamalarni DOM ga qo'llaydi.
 *
 *  Token almashtirish orqali ishlaydi (`document.documentElement.style
 *  .setProperty`), ya'ni qayta render kerak emas — shu sababli "real
 *  vaqtda ko'rish" arzon (D23). Inline qiymat `[data-style]` blokidagi
 *  qiymatdan ustun turadi; `removeProperty` esa uslubning o'z rangini
 *  qaytaradi.
 *
 *  Bu modul hech narsani SAQLAMAYDI — saqlash `CustomizerContext` da.
 */

import type { A11yPrefs, AppearancePrefs } from "@/lib/api";
import {
  AA_TARGET,
  accentInk,
  accentSoft,
  contrast,
  deriveAccent,
  environmentIsDark,
  luminance,
  parseColor,
  readBackgrounds,
  readToken,
  toHex,
  worstContrast,
  type RGB,
} from "./color";

/** Accent bilan bog'liq inline tokenlar — tozalashda shu ro'yxat ishlatiladi. */
const ACCENT_TOKENS = [
  "--rw-accent",
  "--rw-accent-fg",
  "--rw-accent-soft",
  "--rw-accent-ink",
] as const;

export type AccentResult = {
  /** Hosil qilindi va qo'llanildi. */
  ok: boolean;
  /** Accent tugma ustidagi matn kontrasti (`--rw-accent-fg` / `--rw-accent`). */
  button: number | null;
  /** Accent MATN sifatida eng yomon fon ustida (`--rw-accent-ink`). */
  ink: number | null;
  /** O'lchanmagan fon bo'lsa — sabab ko'rsatiladi, "o'tdi" deyilmaydi. */
  error?: string;
};

function clearAccent() {
  for (const token of ACCENT_TOKENS) {
    document.documentElement.style.removeProperty(token);
  }
}

/** Tus va to'yinganlikdan uchta juftlikni hosil qilib qo'llaydi (D45).
 *
 *  Uchta juftlik, bitta emas:
 *    1. `--rw-accent` + `--rw-accent-fg`  — to'ldirilgan tugma
 *    2. `--rw-accent-soft` + `--rw-accent-ink` — rangli chip
 *    3. `--rw-accent-ink` fon ustida — havola matni
 *
 *  `--rw-accent-ink` ikkalasiga ham (fon va chip) sig'ishi kerak, shuning
 *  uchun u IKKALA to'plamga qarshi hosil qilinadi.
 */
export function applyAccent(hue: number, sat: number): AccentResult {
  const backgrounds = readBackgrounds();
  if (!backgrounds.length) {
    clearAccent();
    return { ok: false, button: null, ink: null, error: "fon o'qilmadi" };
  }

  const accent = deriveAccent(hue, sat / 100, backgrounds);
  if (!accent) {
    clearAccent();
    return { ok: false, button: null, ink: null, error: "yorqinlik yetmadi" };
  }

  const dark = environmentIsDark(backgrounds);
  const soft = accentSoft(hue, sat / 100, dark);
  // Ink chip ustida ham, fon ustida ham o'qilishi kerak — eng qat'iy
  // talab qaysi biri bo'lsa, o'shanga moslashadi.
  const ink = deriveAccent(hue, sat / 100, [...backgrounds, soft]) ?? accent;

  // Ink: yorug' mavzuda oq, qorong'ida `--rw-ground` (loyiha an'anasi).
  const lightInk = parseColor("#ffffff") as RGB;
  const groundInk = parseColor(readToken("--rw-ground")) ?? (parseColor("#000000") as RGB);
  const fg = accentInk(accent, lightInk, groundInk);

  const root = document.documentElement.style;
  root.setProperty("--rw-accent", toHex(accent));
  root.setProperty("--rw-accent-fg", toHex(fg));
  root.setProperty("--rw-accent-soft", toHex(soft));
  root.setProperty("--rw-accent-ink", toHex(ink));

  return {
    ok: true,
    button: contrast(fg, accent),
    ink: worstContrast(ink, [...backgrounds, soft]),
  };
}

/** Shrift, o'lcham, zichlik. */
export function applyAppearance(appearance: AppearancePrefs) {
  const root = document.documentElement;

  // Shrift — `null` uslubning o'z shrifti (D14: Editorial/Terminal saqlaydi).
  if (appearance.font) root.dataset.font = appearance.font;
  else delete root.dataset.font;

  // O'lcham — ildiz `font-size` shkalasi; rem asosidagi hamma narsa
  // proporsional kattaradi (D15). 100% da inline qiymat olib tashlanadi.
  if (appearance.size && appearance.size !== 100) {
    root.style.fontSize = `${appearance.size}%`;
  } else {
    root.style.removeProperty("font-size");
  }

  if (appearance.density) root.dataset.density = appearance.density;
  else delete root.dataset.density;
}

/** Qulaylik sozlamalari — hammasi `data-*` atributi orqali, CSS da
 *  qoidalar bor. JS bilan stil yozilmaydi: shunda `globals.css` yagona
 *  haqiqat manbai bo'lib qoladi. */
export function applyA11y(a11y: A11yPrefs) {
  const root = document.documentElement;
  const set = (key: string, value: string | undefined) => {
    if (value) root.dataset[key] = value;
    else delete root.dataset[key];
  };
  set("vision", a11y.vision && a11y.vision !== "normal" ? a11y.vision : undefined);
  set("motion", a11y.motion === "reduce" ? "reduce" : undefined);
  set("targets", a11y.bigTargets ? "big" : undefined);
  set("focus", a11y.strongFocus ? "strong" : undefined);
}

/** Uslub — `StyleContext` ham yozadi, lekin paneldan tanlanganda ham
 *  shu yo'l kerak (qayta render bo'lmasin). */
export function applyStyle(style: string) {
  document.documentElement.dataset.style = style;
}

/** Hamma ko'rinish sozlamalarini bir marta qo'llaydi. */
export function applyAll(appearance: AppearancePrefs, a11y: A11yPrefs): AccentResult {
  applyStyle(appearance.style ?? "clay");
  const accent = appearance.accent
    ? applyAccent(appearance.accent.hue, appearance.accent.sat)
    : (clearAccent(), { ok: true, button: null, ink: null });
  applyAppearance(appearance);
  applyA11y(a11y);
  return accent;
}

/** Panel ko'rsatkichi uchun: shu tus bilan eng yomon kontrast qanday
 *  bo'ladi — QO'LLAMASDAN hisoblaydi (foydalanuvchi hali tanlamagan). */
export function previewAccent(hue: number, sat: number): AccentResult {
  const backgrounds = readBackgrounds();
  if (!backgrounds.length) {
    return { ok: false, button: null, ink: null, error: "fon o'qilmadi" };
  }
  const accent = deriveAccent(hue, sat / 100, backgrounds);
  if (!accent) return { ok: false, button: null, ink: null, error: "yorqinlik yetmadi" };
  const soft = accentSoft(hue, sat / 100, environmentIsDark(backgrounds));
  const ink = deriveAccent(hue, sat / 100, [...backgrounds, soft]) ?? accent;
  const lightInk = parseColor("#ffffff") as RGB;
  const groundInk = parseColor(readToken("--rw-ground")) ?? (parseColor("#000000") as RGB);
  const fg = accentInk(accent, lightInk, groundInk);
  return { ok: true, button: contrast(fg, accent), ink: worstContrast(ink, [...backgrounds, soft]) };
}

/** AA dan o'tadimi. `null` (o'lchanmagan) — o'tmagan hisoblanadi:
 *  o'qib bo'lmagan qiymat "yaxshi" emas. */
export const passes = (ratio: number | null) => ratio !== null && ratio >= AA_TARGET;

export { luminance };
