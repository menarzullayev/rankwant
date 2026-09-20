/** Shablonni ulashish — havola (D22) va JSON fayl (D50).
 *
 *  Havola: sozlamalar URL parametrlariga yoziladi — moderatsiya ham,
 *  saqlash joyi ham kerak emas. Umumiy kutubxona (D22 da rad etilgan)
 *  spam va kontrast nazoratini talab qilardi; havola o'sha ehtiyojning
 *  ko'p qismini arzon qondiradi.
 *
 *  Fayl: havola yetmaydigan ikki hol uchun — (1) zaxira nusxa, (2) uzun
 *  sozlamalarni qo'lda ko'chirish. Havola 200+ belgiga cho'zilib ketadi
 *  va uni chatda saqlash noqulay.
 *
 *  Havolani olgan odam ko'rinishni **ko'radi** va xohlasa shablon qilib
 *  saqlaydi. Parametrlar o'qilgach manzildan olib tashlanadi
 *  (`history.replaceState`) — aks holda har yuklanishda qayta qo'llanib,
 *  odam o'z sozlamasini o'zgartira olmay qolardi.
 */

import type { A11yPrefs, AppearancePrefs, ThemeTemplate } from "@/lib/api";
import {
  clampLineHeight,
  clampScale,
  clampSize,
  clampTracking,
  clampWidth,
} from "@/lib/theme/typography";
import { clampNavMode, clampNavShape } from "@/layout/nav-config";
import { clampVerdictVariant } from "@/lib/theme/verdict";
import { clampStatusVariant } from "@/lib/theme/status";
import { clampLoadingVariant } from "@/lib/theme/loading";
import { clampIconPack } from "@/lib/theme/icon-packs";
import { clampOverlayVariant } from "@/lib/theme/overlay";
import { clampFormVariant } from "@/lib/theme/form";
import { DEFAULT_CARD, DEFAULT_PATTERN } from "@/lib/theme/apply";

/** URL da saqlanadigan maydonlar. `KEYS` — tozalash uchun ham ishlatiladi. */
const KEYS = [
  "style",
  // Not an appearance field: the theme mode lives in `User.theme`. It is
  // listed here so that a shared link carries it and gets cleaned up too.
  "theme",
  "accent",
  "font",
  "fontHeading",
  "size",
  "scale",
  "lineHeight",
  "tracking",
  "width",
  "density",
  "navMode",
  "navShape",
  "card",
  "pattern",
  "verdictStyle",
  "statusStyle",
  "loadingStyle",
  "iconPack",
  "overlayStyle",
  "formStyle",
] as const;

const DENSITIES = ["compact", "comfortable", "spacious"] as const;
const FONTS = ["inter", "jakarta", "roboto", "dm-sans", "lexend"] as const;
const CARDS = ["default", "outline", "flat", "soft", "square"] as const;
const PATTERNS = ["none", "grid", "dots", "diagonal", "mesh"] as const;

type ThemeMode = NonNullable<ThemeTemplate["theme"]>;

const isThemeMode = (value: unknown): value is ThemeMode =>
  value === "light" || value === "dark" || value === "system";

/** Ko'rinishni URL ga yozadi. Standart qiymatlar tushib qoladi — havola
 *  qisqa bo'lsin va faqat o'zgartirilgan narsa ko'rinsin.
 *
 *  `theme` is written only when the sharer picked light or dark. `system`
 *  is the default, so it drops out like the other defaults and the
 *  recipient keeps their own mode. */
export function encodeAppearance(
  appearance: AppearancePrefs,
  theme?: ThemeMode,
): string {
  const params = new URLSearchParams();
  if (appearance.style) params.set("style", appearance.style);
  if (theme === "light" || theme === "dark") params.set("theme", theme);
  if (appearance.accent) {
    params.set("accent", `${appearance.accent.hue}-${appearance.accent.sat}`);
  }
  if (appearance.font) params.set("font", appearance.font);
  if (appearance.fontHeading) params.set("fontHeading", appearance.fontHeading);
  if (appearance.size && appearance.size !== 100) {
    params.set("size", String(appearance.size));
  }
  if (appearance.scale && appearance.scale !== 1) {
    params.set("scale", String(appearance.scale));
  }
  if (appearance.lineHeight && appearance.lineHeight !== 1) {
    params.set("lineHeight", String(appearance.lineHeight));
  }
  if (appearance.tracking) {
    params.set("tracking", String(appearance.tracking));
  }
  if (appearance.width && appearance.width !== 1400) {
    params.set("width", String(appearance.width));
  }
  if (appearance.density && appearance.density !== "comfortable") {
    params.set("density", appearance.density);
  }
  if (appearance.navMode && appearance.navMode !== "sidenav") {
    params.set("navMode", appearance.navMode);
  }
  if (appearance.navShape && appearance.navShape !== "default") {
    params.set("navShape", appearance.navShape);
  }
  if (appearance.card && appearance.card !== "default") {
    params.set("card", appearance.card);
  }
  if (appearance.pattern && appearance.pattern !== "none") {
    params.set("pattern", appearance.pattern);
  }
  if (appearance.verdictStyle && appearance.verdictStyle !== "auto") {
    params.set("verdictStyle", appearance.verdictStyle);
  }
  if (appearance.statusStyle && appearance.statusStyle !== "auto") {
    params.set("statusStyle", appearance.statusStyle);
  }
  if (appearance.loadingStyle && appearance.loadingStyle !== "spinner") {
    params.set("loadingStyle", appearance.loadingStyle);
  }
  if (appearance.iconPack && appearance.iconPack !== "lucide") {
    params.set("iconPack", appearance.iconPack);
  }
  if (appearance.overlayStyle && appearance.overlayStyle !== "qogoz") {
    params.set("overlayStyle", appearance.overlayStyle);
  }
  if (appearance.formStyle && appearance.formStyle !== "maydon") {
    params.set("formStyle", appearance.formStyle);
  }
  return params.toString();
}

/** URL dan ko'rinishni o'qiydi. Hech narsa yo'q bo'lsa — `null`.
 *
 *  Notanish qiymatlar JIMGINA tashlab yuboriladi: begona havola butun
 *  ko'rinishni buzmasligi kerak, lekin uni qo'llash ham mumkin emas.
 *  ⚠️ Har bir maydon `clamp*` orqali o'tadi — havola qo'lda tahrirlanishi
 *  mumkin, ya'ni bu ishonchsiz manba. */
export function decodeAppearance(search: string): AppearancePrefs | null {
  const params = new URLSearchParams(search);
  if (!KEYS.some((key) => params.has(key))) return null;

  const out: AppearancePrefs = {};
  const style = params.get("style");
  if (style && /^[a-z-]{1,20}$/.test(style)) out.style = style;

  const accent = params.get("accent");
  if (accent) {
    const match = accent.match(/^(\d{1,3})-(\d{1,3})$/);
    if (match) {
      const hue = Number(match[1]);
      const sat = Number(match[2]);
      if (hue <= 359 && sat <= 100) out.accent = { hue, sat };
    }
  }

  const font = params.get("font");
  if (font && (FONTS as readonly string[]).includes(font)) out.font = font;

  const fontHeading = params.get("fontHeading");
  if (fontHeading && (FONTS as readonly string[]).includes(fontHeading)) {
    out.fontHeading = fontHeading;
  }

  if (params.has("size")) out.size = clampSize(Number(params.get("size")));
  if (params.has("scale")) out.scale = clampScale(Number(params.get("scale")));
  if (params.has("lineHeight")) {
    out.lineHeight = clampLineHeight(Number(params.get("lineHeight")));
  }
  if (params.has("tracking")) {
    out.tracking = clampTracking(Number(params.get("tracking")));
  }
  if (params.has("width")) out.width = clampWidth(Number(params.get("width")));

  const density = params.get("density");
  if (density && (DENSITIES as readonly string[]).includes(density)) {
    out.density = density as AppearancePrefs["density"];
  }

  if (params.has("navMode")) out.navMode = clampNavMode(params.get("navMode"));
  if (params.has("navShape")) {
    out.navShape = clampNavShape(params.get("navShape"));
  }

  const card = params.get("card");
  if (card && (CARDS as readonly string[]).includes(card)) {
    out.card = card as AppearancePrefs["card"];
  }
  const pattern = params.get("pattern");
  if (pattern && (PATTERNS as readonly string[]).includes(pattern)) {
    out.pattern = pattern as AppearancePrefs["pattern"];
  }

  // Verdikt va holat ko'rinishlari — notanish qiymat standartga tushadi
  // (`clamp*`), ya'ni begona havola sozlamani buza olmaydi.
  if (params.has("verdictStyle")) {
    out.verdictStyle = clampVerdictVariant(params.get("verdictStyle"));
  }
  if (params.has("statusStyle")) {
    out.statusStyle = clampStatusVariant(params.get("statusStyle"));
  }
  if (params.has("loadingStyle")) {
    out.loadingStyle = clampLoadingVariant(params.get("loadingStyle"));
  }
  if (params.has("iconPack")) {
    out.iconPack = clampIconPack(params.get("iconPack"));
  }
  if (params.has("overlayStyle")) {
    out.overlayStyle = clampOverlayVariant(params.get("overlayStyle"));
  }
  if (params.has("formStyle")) {
    out.formStyle = clampFormVariant(params.get("formStyle"));
  }

  return Object.keys(out).length ? out : null;
}

/** Reads the theme mode from a shared link; `null` when it is absent or
 *  not a known mode. Kept apart from `decodeAppearance` because the mode
 *  is stored in `User.theme`, not in the appearance group. */
export function decodeTheme(search: string): ThemeMode | null {
  const theme = new URLSearchParams(search).get("theme");
  return isThemeMode(theme) ? theme : null;
}

/** Joriy manzilga ko'rinish parametrlarini qo'shib qaytaradi. */
export function shareUrl(appearance: AppearancePrefs, theme?: ThemeMode): string {
  const url = new URL(window.location.href);
  for (const key of KEYS) url.searchParams.delete(key);
  const encoded = encodeAppearance(appearance, theme);
  if (encoded) {
    for (const [key, value] of new URLSearchParams(encoded)) {
      url.searchParams.set(key, value);
    }
  }
  return url.toString();
}

/** Ko'rinish parametrlarini manzildan olib tashlaydi — qo'llangandan
 *  keyin qayta qo'llanilmasin. */
export function stripAppearance(): string {
  const url = new URL(window.location.href);
  for (const key of KEYS) url.searchParams.delete(key);
  return url.pathname + url.search + url.hash;
}

/* ── JSON fayl (D50) ──────────────────────────────────────────────────── */

/** Fayl formati versiyasi. Kelajakda maydon nomi o'zgarsa, eski fayllarni
 *  tanish uchun kerak — versiyasiz fayl "buzuq" dan ajratilmaydi. */
export const EXPORT_VERSION = 1;

export type ExportedAppearance = {
  version: number;
  exportedAt: string;
  appearance: AppearancePrefs;
  a11y: A11yPrefs;
  /** Optional, so the version stays 1: older files simply lack it and
   *  older clients drop it as an unknown key. */
  theme?: ThemeMode;
};

/** Ko'rinishni yuklab olinadigan JSON satriga aylantiradi. */
export function exportAppearance(
  appearance: AppearancePrefs,
  a11y: A11yPrefs,
  theme?: ThemeMode,
): string {
  const payload: ExportedAppearance = {
    version: EXPORT_VERSION,
    exportedAt: new Date().toISOString(),
    appearance,
    a11y,
    ...(theme ? { theme } : {}),
  };
  return JSON.stringify(payload, null, 2);
}

export type ImportResult =
  | { ok: true; appearance: AppearancePrefs; a11y: A11yPrefs; theme?: ThemeMode }
  | { ok: false; error: "parse" | "shape" | "version" };

/** JSON satridan ko'rinishni tiklaydi.
 *
 *  ⚠️ Fayl — ishonchsiz manba: har bir maydon `clamp*` dan o'tadi va
 *  notanish kalitlar tashlab yuboriladi. Faylni qo'lda tahrirlab
 *  `size: 99999` yozish mumkin, ya'ni tekshiruvsiz qo'llash sahifani
 *  o'qib bo'lmas holga keltiradi (o'lchandi: SSR script'da ham shu
 *  sababdan chegara qo'yilgan). */
export function importAppearance(raw: string): ImportResult {
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch {
    return { ok: false, error: "parse" };
  }
  if (!data || typeof data !== "object") return { ok: false, error: "shape" };

  const row = data as Partial<ExportedAppearance>;
  if (row.version !== undefined && row.version > EXPORT_VERSION) {
    return { ok: false, error: "version" };
  }
  if (!row.appearance || typeof row.appearance !== "object") {
    return { ok: false, error: "shape" };
  }

  const a = row.appearance as AppearancePrefs;
  const appearance: AppearancePrefs = {};
  if (typeof a.style === "string" && /^[a-z-]{1,20}$/.test(a.style)) {
    appearance.style = a.style;
  }
  if (a.accent && typeof a.accent === "object") {
    const hue = Number(a.accent.hue);
    const sat = Number(a.accent.sat);
    if (Number.isFinite(hue) && Number.isFinite(sat) && hue <= 359 && sat <= 100) {
      appearance.accent = { hue: Math.round(hue), sat: Math.round(sat) };
    }
  }
  if (typeof a.font === "string" && (FONTS as readonly string[]).includes(a.font)) {
    appearance.font = a.font;
  } else if (a.font === null) {
    appearance.font = null;
  }
  if (
    typeof a.fontHeading === "string" &&
    (FONTS as readonly string[]).includes(a.fontHeading)
  ) {
    appearance.fontHeading = a.fontHeading;
  } else if (a.fontHeading === null) {
    appearance.fontHeading = null;
  }
  appearance.size = clampSize(a.size);
  appearance.scale = clampScale(a.scale);
  appearance.lineHeight = clampLineHeight(a.lineHeight);
  appearance.tracking = clampTracking(a.tracking);
  appearance.width = clampWidth(a.width);
  if (typeof a.density === "string" && (DENSITIES as readonly string[]).includes(a.density)) {
    appearance.density = a.density as AppearancePrefs["density"];
  }
  appearance.navMode = clampNavMode(a.navMode);
  appearance.navShape = clampNavShape(a.navShape);
  appearance.card =
    typeof a.card === "string" && (CARDS as readonly string[]).includes(a.card)
      ? a.card
      : DEFAULT_CARD;
  appearance.pattern =
    typeof a.pattern === "string" &&
    (PATTERNS as readonly string[]).includes(a.pattern)
      ? a.pattern
      : DEFAULT_PATTERN;
  // `clamp*` — fayl qo'lda tahrirlanishi mumkin, ya'ni ishonchsiz manba.
  appearance.verdictStyle = clampVerdictVariant(a.verdictStyle);
  appearance.statusStyle = clampStatusVariant(a.statusStyle);
  appearance.loadingStyle = clampLoadingVariant(a.loadingStyle);
  appearance.iconPack = clampIconPack(a.iconPack);
  appearance.overlayStyle = clampOverlayVariant(a.overlayStyle);
  appearance.formStyle = clampFormVariant(a.formStyle);

  const k = (row.a11y ?? {}) as A11yPrefs;
  const a11y: A11yPrefs = {
    vision:
      k.vision === "protan" || k.vision === "tritan" ? k.vision : "normal",
    motion:
      k.motion === "full" || k.motion === "mild" || k.motion === "off"
        ? k.motion
        : "system",
    bigTargets: Boolean(k.bigTargets),
    strongFocus: Boolean(k.strongFocus),
  };

  // An unknown mode is dropped, not rejected: the rest of the file is
  // still usable, and applying it simply keeps the current mode.
  return isThemeMode(row.theme)
    ? { ok: true, appearance, a11y, theme: row.theme }
    : { ok: true, appearance, a11y };
}
