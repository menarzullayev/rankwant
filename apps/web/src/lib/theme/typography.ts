/** Tipografiya shkalasi — moslashuvchan va markazlashtirilgan (D45).
 *
 * Nega alohida fayl: ilgari o'lchamlar ikki joyda edi — `globals.css` dagi
 * `--text-theme-*` (qat'iy piksellar) va `apply.ts` dagi ildiz `font-size`
 * foizi (faqat 90/100/110/120). Ikkalasi bir-birini bilmasdi: foiz hamma
 * narsani birdan kattalashtirardi, shkala esa umuman sozlanmasdi.
 *
 * Bu fayl — yagona manba. Shkala **nisbiy** (`rem`), ildiz esa **foiz**:
 * shuning uchun bitta qiymatni o'zgartirish butun tipografikani
 * proporsional o'zgartiradi, hech narsa qotib qolmaydi.
 *
 * `size` — erkin diapazon (kep.uz dagi slider kabi): 75 % dan 150 % gacha.
 * `scale` — qadamlar orasidagi nisbat (kichik/yirik shrift farqi).
 */

/** Shkala darajasi — kichikdan kattaga. */
export type TypeStep =
  | "xs"
  | "sm"
  | "base"
  | "lg"
  | "xl"
  | "2xl"
  | "3xl"
  | "4xl";

/** Bitta darajaning to'liq tavsifi. */
export type TypeStepDef = {
  /** `rem` da — ildiz `font-size` ga nisbatan, ya'ni `size` ga ergashadi. */
  size: number;
  /** Raqamsiz ko'paytirgich (1.5 = 150 %). */
  lineHeight: number;
  /** 400–800. */
  weight: number;
  /** `em` da manfiy qiymat — katta sarlavhalarda harflar siqiqroq. */
  letterSpacing: number;
};

/** Asosiy shkala — 1.250 (major third) nisbatiga yaqin.
 *
 *  O'lchamlari `rem`: ildiz 16 px bo'lganda 0.75 rem = 12 px, 2.5 rem = 40 px.
 *  `lineHeight` kichik o'lchamlarda kengroq (1.6), kattalarda siqiqroq (1.1) —
 *  aks holda katta sarlavha ikki qatorga bo'linib ketadi. */
export const TYPE_SCALE: Record<TypeStep, TypeStepDef> = {
  xs: { size: 0.75, lineHeight: 1.6, weight: 400, letterSpacing: 0 },
  sm: { size: 0.875, lineHeight: 1.55, weight: 400, letterSpacing: 0 },
  base: { size: 1, lineHeight: 1.5, weight: 400, letterSpacing: 0 },
  lg: { size: 1.125, lineHeight: 1.45, weight: 500, letterSpacing: -0.005 },
  xl: { size: 1.25, lineHeight: 1.35, weight: 600, letterSpacing: -0.01 },
  "2xl": { size: 1.5, lineHeight: 1.25, weight: 600, letterSpacing: -0.015 },
  "3xl": { size: 1.875, lineHeight: 1.2, weight: 700, letterSpacing: -0.02 },
  "4xl": { size: 2.25, lineHeight: 1.1, weight: 700, letterSpacing: -0.025 },
};

/** Tayyor matn uslublari — shkala darajasiga murojaat.
 *  Yangi joyda `text-[13px]` yozish o'rniga shu ro'yxatdan olinadi. */
export const TEXT_STYLES = {
  caption: "xs",
  bodySm: "sm",
  body: "base",
  bodyLg: "lg",
  label: "sm",
  h4: "lg",
  h3: "xl",
  h2: "2xl",
  h1: "3xl",
  display: "4xl",
} as const satisfies Record<string, TypeStep>;

/** Ildiz o'lchami chegaralari — kep.uz dagi 12–20 px diapazonining
 *  proporsional ko'rinishi. 100 % = 16 px. */
export const SIZE_MIN = 75;
export const SIZE_MAX = 150;
export const SIZE_STEP = 5;
export const SIZE_DEFAULT = 100;

/** Qadamlar ro'yxati — panelda shu tartibda chiqadi. */
export const SIZE_STEPS: number[] = (() => {
  const out: number[] = [];
  for (let v = SIZE_MIN; v <= SIZE_MAX; v += SIZE_STEP) out.push(v);
  return out;
})();

/** Diapazonga soladi va qadamga yaxlitlaydi — localStorage'dan kelgan
 *  buzuk qiymat butun shkalani buzmasin. */
export function clampSize(value: number | undefined): number {
  if (typeof value !== "number" || !Number.isFinite(value)) return SIZE_DEFAULT;
  const snapped = Math.round(value / SIZE_STEP) * SIZE_STEP;
  return Math.min(SIZE_MAX, Math.max(SIZE_MIN, snapped));
}

/** Shkala zichligi: 1 = odatiy. Kattaroq qiymat qadamlar orasini ochadi
 *  (katta sarlavha yanada kattaroq), kichigi — yig'adi. */
export const SCALE_MIN = 0.9;
export const SCALE_MAX = 1.15;
export const SCALE_DEFAULT = 1;

export function clampScale(value: number | undefined): number {
  if (typeof value !== "number" || !Number.isFinite(value)) return SCALE_DEFAULT;
  return Math.min(SCALE_MAX, Math.max(SCALE_MIN, Math.round(value * 100) / 100));
}

/** Darajaning yakuniy `rem` qiymati — zichlik hisobga olingan.
 *  `base` (1 rem) qotib qoladi: u tayanch nuqta, aks holda zichlik
 *  o'zgarganda butun sahifa siljiydi. */
function stepRem(step: TypeStep, scale: number): number {
  const def = TYPE_SCALE[step];
  if (step === "base") return def.size;
  const ratio = def.size / TYPE_SCALE.base.size;
  // `base` dan uzoqlashgan sari zichlik kuchliroq ta'sir qiladi.
  const eased = 1 + (ratio - 1) * scale;
  return Math.round(eased * 1000) / 1000;
}

export type TypographyPrefs = {
  /** Ildiz `font-size` foizi — 75…150 (D45). */
  size?: number;
  /** Shkala zichligi — 0.90…1.15. */
  scale?: number;
  /** Qator balandligi ko'paytirgichi — 0.9…1.4 (D47). 1 = uslubning o'zi. */
  lineHeight?: number;
  /** Harf oralig'i qo'shimchasi, `em` — −0.02…0.06 (D47). 0 = o'zgarmagan. */
  tracking?: number;
};

export const LINE_HEIGHT_MIN = 0.9;
export const LINE_HEIGHT_MAX = 1.4;
export const LINE_HEIGHT_DEFAULT = 1;

export const TRACKING_MIN = -0.02;
export const TRACKING_MAX = 0.06;
export const TRACKING_DEFAULT = 0;

/** Kontent kengligi (D48) — sahifaning o'qish kengligi. */
export const WIDTH_MIN = 1000;
export const WIDTH_MAX = 1800;
export const WIDTH_STEP = 100;
export const WIDTH_DEFAULT = 1400;

export function clampWidth(value: number | undefined): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return WIDTH_DEFAULT;
  }
  const snapped = Math.round(value / WIDTH_STEP) * WIDTH_STEP;
  return Math.min(WIDTH_MAX, Math.max(WIDTH_MIN, snapped));
}

export function clampLineHeight(value: number | undefined): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return LINE_HEIGHT_DEFAULT;
  }
  return Math.min(
    LINE_HEIGHT_MAX,
    Math.max(LINE_HEIGHT_MIN, Math.round(value * 100) / 100),
  );
}

export function clampTracking(value: number | undefined): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return TRACKING_DEFAULT;
  }
  return Math.min(
    TRACKING_MAX,
    Math.max(TRACKING_MIN, Math.round(value * 1000) / 1000),
  );
}

/** Mavjud Tailwind tokenlari — `globals.css` dagi ASL qiymatlar.
 *
 *  ⚠️ Bu yerda `rem` EMAS, `px` turadi va asl qiymat aynan takrorlanadi.
 *  Sabab o'lchandi: birinchi urinishda ular `rem` bilan yozilgan edi va
 *  natija TESKARI chiqdi — `×0.9` da h1 23.2 px, `×1.1` da 24.8 px
 *  (ya'ni standart 30 px dan kichik). Sabab: `--text-title-sm` CSS da
 *  `30px`, `rem` bilan yozilganda esa `1.5rem = 24px` bo'lib qolardi.
 *  Endi asl px saqlanadi va faqat nisbat qo'llanadi. */
const LEGACY_TOKENS: { key: string; px: number; lineHeightPx: number }[] = [
  { key: "--text-theme-xs", px: 12, lineHeightPx: 18 },
  { key: "--text-theme-sm", px: 14, lineHeightPx: 20 },
  { key: "--text-theme-xl", px: 20, lineHeightPx: 30 },
  { key: "--text-title-sm", px: 30, lineHeightPx: 38 },
  { key: "--text-title-md", px: 36, lineHeightPx: 44 },
];

/** Bitta px qiymatga zichlikni qo'llaydi.
 *
 *  `base` (16 px) qotib qoladi — u tayanch nuqta. Undan uzoqroq turgan
 *  o'lcham zichlikka ko'proq ergashadi: 12 px deyarli o'zgarmaydi,
 *  36 px sezilarli o'sadi. Shuning uchun shkala "ochiladi" yoki
 *  "yig'iladi", hammasi birga siljimaydi. */
function scalePx(px: number, scale: number): number {
  const ratio = px / 16;
  const eased = 1 + (ratio - 1) * scale;
  return Math.round(eased * 16 * 100) / 100;
}

/** Shkalani `:root` ga yozadi.
 *
 *  Ikkita chiqish bor:
 *  1. `--rw-text-*` — to'liq shkala (`rem`), yangi joylar uchun;
 *  2. `--text-theme-*` / `--text-title-*` — `globals.css` dagi mavjud
 *     Tailwind tokenlari (`px`). Ular qayta yoziladi, shuning uchun eski
 *     `text-theme-sm` ni ishlatgan yuzlab joy ham o'zgarishni sezadi.
 *
 *  Standart qiymatda inline uslub olib tashlanadi — CSS dagi asl qiymat
 *  qaytadi (xuddi `accent` dagi kabi, D11). */
export function applyTypography(
  root: HTMLElement,
  prefs: TypographyPrefs,
): void {
  const size = clampSize(prefs.size);
  const scale = clampScale(prefs.scale);
  const lineHeight = clampLineHeight(prefs.lineHeight);
  const tracking = clampTracking(prefs.tracking);
  const plain =
    size === SIZE_DEFAULT &&
    scale === SCALE_DEFAULT &&
    lineHeight === LINE_HEIGHT_DEFAULT &&
    tracking === TRACKING_DEFAULT;

  if (plain) {
    for (const key of Object.keys(CSS_KEYS)) root.style.removeProperty(key);
    root.style.removeProperty("font-size");
    root.style.removeProperty("--rw-type-scale");
    delete root.dataset.typeScale;
    return;
  }

  // Ildiz — rem hisoblanadigan tayanch. `size` foizi aynan shu yerda.
  root.style.fontSize = `${size}%`;
  root.style.setProperty("--rw-type-scale", String(scale));
  if (scale !== SCALE_DEFAULT) root.dataset.typeScale = String(scale);
  else delete root.dataset.typeScale;

  for (const step of Object.keys(TYPE_SCALE) as TypeStep[]) {
    const def = TYPE_SCALE[step];
    const rem = stepRem(step, scale);
    root.style.setProperty(`--rw-text-${step}`, `${rem}rem`);
    // Qator balandligi va harf oralig'i (D47) — ko'paytirgich shkalaning
    // O'Z qiymatiga qo'llanadi, ya'ni uslub nisbati saqlanadi.
    root.style.setProperty(
      `--rw-text-${step}--line-height`,
      String(Math.round(def.lineHeight * lineHeight * 1000) / 1000),
    );
    root.style.setProperty(`--rw-text-${step}--weight`, String(def.weight));
    root.style.setProperty(
      `--rw-text-${step}--tracking`,
      `${Math.round((def.letterSpacing + tracking) * 10000) / 10000}em`,
    );
  }

  // Mavjud Tailwind tokenlari — asl px saqlanadi, faqat nisbat qo'llanadi.
  // Chiziq balandligi raqamsiz nisbat sifatida beriladi (asl juftlikdan
  // hisoblanadi), shunda u o'lchamga proporsional ergashadi.
  for (const token of LEGACY_TOKENS) {
    root.style.setProperty(token.key, `${scalePx(token.px, scale)}px`);
    const ratio = (token.lineHeightPx / token.px) * lineHeight;
    root.style.setProperty(
      `${token.key}--line-height`,
      String(Math.round(ratio * 1000) / 1000),
    );
  }
}

/** `applyTypography` olib tashlashi kerak bo'lgan barcha kalit —
 *  ro'yxat qo'lda emas, shkaladan hosil qilinadi: yangi daraja qo'shilsa
 *  tozalash ham o'zi kengayadi. */
const CSS_KEYS: Record<string, true> = (() => {
  const out: Record<string, true> = {
    "--text-theme-xs": true,
    "--text-theme-xs--line-height": true,
    "--text-theme-sm": true,
    "--text-theme-sm--line-height": true,
    "--text-theme-xl": true,
    "--text-theme-xl--line-height": true,
    "--text-title-sm": true,
    "--text-title-sm--line-height": true,
    "--text-title-md": true,
    "--text-title-md--line-height": true,
  };
  for (const step of Object.keys(TYPE_SCALE) as TypeStep[]) {
    out[`--rw-text-${step}`] = true;
    out[`--rw-text-${step}--line-height`] = true;
    out[`--rw-text-${step}--weight`] = true;
    out[`--rw-text-${step}--tracking`] = true;
  }
  return out;
})();

/** Panel uchun: joriy foizda 1 rem necha piksel. */
export function remToPx(value: number): number {
  return Math.round(value * 16 * 100) / 100;
}
