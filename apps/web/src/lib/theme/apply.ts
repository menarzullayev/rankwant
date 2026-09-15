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
import { clampNavMode, clampNavShape } from "@/layout/nav-config";
import { applyTypography, clampWidth } from "@/lib/theme/typography";
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

/** Accent hosil bo'lmaganda sabab. Matn EMAS: bu modul sof hisoblash
 *  qatlami, tarjima esa ko'rsatish joyida (`errorText()`) qilinadi.
 *  Kodlar `error.<code>` kalitlariga to'g'ri keladi — `messages.ts` dagi
 *  umumiy xato mexanizmi bilan bir xil yo'l.
 *  Ilgari bu yerda tayyor o'zbekcha satr qaytarilardi va u 9 tilning
 *  hech birida tarjima qilinmasdi (o'lchandi). */
export type AccentError = "ground_unreadable" | "contrast_unreachable";

export type AccentResult = {
  /** Hosil qilindi va qo'llanildi. */
  ok: boolean;
  /** Accent tugma ustidagi matn kontrasti (`--rw-accent-fg` / `--rw-accent`). */
  button: number | null;
  /** Accent MATN sifatida eng yomon fon ustida (`--rw-accent-ink`). */
  ink: number | null;
  /** O'lchanmagan fon bo'lsa — sabab ko'rsatiladi, "o'tdi" deyilmaydi. */
  error?: AccentError;
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
    return { ok: false, button: null, ink: null, error: "ground_unreadable" };
  }

  const accent = deriveAccent(hue, sat / 100, backgrounds);
  if (!accent) {
    clearAccent();
    return { ok: false, button: null, ink: null, error: "contrast_unreachable" };
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

  // O'lcham va tipografik shkala — `typography.ts` yagona manba (D45).
  // Ildiz `font-size` foizi ham, `--text-*` tokenlari ham shu yerda.
  applyTypography(root, appearance);

  if (appearance.density) root.dataset.density = appearance.density;
  else delete root.dataset.density;

  // Navigatsiya (D46). Shakl faqat topnav'ga ta'sir qiladi, lekin atribut
  // har doim yoziladi — sidenav'ga o'tganda tanlov saqlanib qolsin.
  root.dataset.nav = clampNavMode(appearance.navMode);
  root.dataset.navShape = clampNavShape(appearance.navShape);

  // Kontent kengligi (D48). `AppShell` dagi `max-w-[1400px]` o'rniga
  // o'zgaruvchi — Tailwind sinfi qotib qolgan edi.
  root.style.setProperty("--rw-content-width", `${clampWidth(appearance.width)}px`);
}

/** Rang ajratolmaslik uchun TUSLAR (D44).
 *
 *  Protanopiya va deuteranopiyada qizil-yashil o'qi yo'qoladi, ko'k-sariq
 *  qoladi — shuning uchun holatlar shu o'qqa ko'chiriladi. Tritanopiyada
 *  aksincha. Bu SIMULYATSIYA emas: rang ajratolmaydigan odam o'z holatini
 *  allaqachon shunday ko'radi, unga palitraning MOSLASHGANI kerak. */
const VISION_HUES = {
  protan: { ok: 210, warn: 55, bad: 32 },
  tritan: { ok: 140, warn: 320, bad: 10 },
} as const;

/** Holat → (ink, soft) token juftliklari. */
const STATE_TOKENS = {
  ok: ["--rw-ok-ink", "--rw-ok-soft"],
  warn: ["--rw-warn-ink", "--rw-warn-soft"],
  bad: ["--rw-bad-ink", "--rw-bad-soft"],
} as const;

/** Qulaylik sozlamalari.
 *
 *  Uchtasi `data-*` atributi orqali (CSS da qoidalar bor). Rang
 *  ajratolmaslik palitrasi esa INLINE yoziladi: u har palitrada boshqa
 *  fon ustida turadi va CSS bilan statik qiymat yozib bo'lmaydi —
 *  `[data-style].dark` bloklari har qanday `[data-vision]` qoidasidan
 *  xoslikda ustun, ya'ni statik yechim jimgina ishlamasdi. */
export function applyA11y(a11y: A11yPrefs) {
  const root = document.documentElement;
  const set = (key: string, value: string | undefined) => {
    if (value) root.dataset[key] = value;
    else delete root.dataset[key];
  };
  set("vision", a11y.vision && a11y.vision !== "normal" ? a11y.vision : undefined);
  // `system` — OS sozlamasiga ergashadi, ya'ni atribut yozilmaydi (D49).
  set(
    "motion",
    a11y.motion && a11y.motion !== "system" ? a11y.motion : undefined,
  );
  set("targets", a11y.bigTargets ? "big" : undefined);
  set("focus", a11y.strongFocus ? "strong" : undefined);

  const inks = Object.values(STATE_TOKENS).map(([ink]) => ink);
  if (!a11y.vision || a11y.vision === "normal") {
    for (const token of inks) root.style.removeProperty(token);
    return;
  }

  const hues = VISION_HUES[a11y.vision];
  const backgrounds = readBackgrounds();
  if (!backgrounds.length) {
    // O'lchab bo'lmadi — palitra o'zgartirilmaydi. Yolg'on rang
    // qo'yishdan ko'ra tegmaslik xavfsizroq.
    for (const token of inks) root.style.removeProperty(token);
    return;
  }
  for (const state of ["ok", "warn", "bad"] as const) {
    const [inkToken, softToken] = STATE_TOKENS[state];
    const soft = parseColor(readToken(softToken));
    const targets = soft ? [...backgrounds, soft] : backgrounds;
    const derived = deriveAccent(hues[state], 0.9, targets);
    if (derived) root.style.setProperty(inkToken, toHex(derived));
    else root.style.removeProperty(inkToken);
  }
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
    return { ok: false, button: null, ink: null, error: "ground_unreadable" };
  }
  const accent = deriveAccent(hue, sat / 100, backgrounds);
  if (!accent) return { ok: false, button: null, ink: null, error: "contrast_unreachable" };
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
