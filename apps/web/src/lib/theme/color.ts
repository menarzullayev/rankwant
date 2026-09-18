/** Rang matematikasi — `tools/check_contrast.py` bilan AYNI formula.
 *
 *  Panelning jonli kontrast ko'rsatkichi shu funksiyalarga tayanadi, ya'ni
 *  CI va brauzer bir xil raqam beradi (D12 — kafolat ikki qavatli: CI
 *  statik 18 palitrani, panel esa foydalanuvchi kombinatsiyasini o'lchaydi).
 *
 *  Formula WCAG 2.x relative luminance:
 *
 *      lin(c) = c/12.92                c ≤ 0.03928
 *      lin(c) = ((c+0.055)/1.055)^2.4  aks holda
 *      L      = 0.2126·R + 0.7152·G + 0.0722·B
 *      ratio  = (L_hi + 0.05) / (L_lo + 0.05)
 *
 *  Metod ma'lum qiymatlarda sinandi: `#000000`/`#ffffff` = 21.00,
 *  `#767676`/`#ffffff` = 4.54 (AA chegarasi), `#777777`/`#ffffff` = 4.48.
 */

export type RGB = [number, number, number];

/** AA chegarasi. Zaxira bilan olamiz: hosil qilingan rang chegarada
 *  qolmasin, ya'ni yaxlitlash uni ostiga tushirmasin. */
export const AA = 4.5;
export const AA_TARGET = 4.6;

export function srgbLinear(v: number): number {
  const c = v / 255;
  return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** Rang va uning shaffofligi. `alpha` — 0…1. */
export type RGBA = [number, number, number, number];

/** Uslub tokenidagi HAR QANDAY rang yozuvi → `[r, g, b, a]`.
 *
 *  Qo'llab-quvvatlanadigan shakllar va nega ularning har biri kerak
 *  (hammasi `globals.css` dan olingan, 2026-09-18 da o'lchangan):
 *
 *   - `#rgb` / `#rgba` — `flat` da `--rw-surface: #fff`;
 *   - `#rrggbb` / `#rrggbbaa` — `--rw-hover: #ffffff14` kabi qatlamlar;
 *   - `rgb()` / `rgba()` — `glass` da `rgba(0, 0, 0, .62)`;
 *   - `linear-gradient(...)` — `glass` da `--rw-ground` gradient, BIRINCHI
 *     rang olinadi: fon o'lchovi uchun bitta vakil rang yetarli, gradientning
 *     o'rtasi esa yorqinlik bo'yicha chetlaridan uzoqqa ketmaydi.
 *
 *  ⚠️ Bu ro'yxat 2026-09-18 gacha faqat `#rrggbb` va `rgb()` edi. Natijada
 *  `glass` va `swiss` uslublarida `readBackgrounds()` bo'sh qaytardi, panel
 *  esa buni «rang AA dan o'tmadi» deb ko'rsatardi — aslida kontrast
 *  UMUMAN o'lchanmagan edi va accent tanlash o'lik edi
 *  (`docs/research/2026-09-18-appearance-audit/BOARD.md`, APP-1).
 */
export function parseRgba(value: string): RGBA | null {
  const text = value.trim();
  const gradient = text.match(/(?:linear|radial|conic)-gradient\((.*)\)/s);
  if (gradient) {
    // Birinchi rang: `135deg, #341d65 0%, …` — burchakdan keyingi bo'lak.
    const first = gradient[1].match(
      /(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\))/,
    );
    return first ? parseRgba(first[1]) : null;
  }
  const hex = text.match(/^#([0-9a-fA-F]{3,8})$/);
  if (hex) {
    const h = hex[1];
    const wide = h.length > 4;
    const size = wide ? 2 : 1;
    if (h.length !== (wide ? 6 : 3) && h.length !== (wide ? 8 : 4)) return null;
    const at = (i: number) => {
      const part = h.slice(i * size, i * size + size);
      return parseInt(wide ? part : part + part, 16);
    };
    const alpha = h.length === (wide ? 8 : 4) ? at(3) / 255 : 1;
    return [at(0), at(1), at(2), alpha];
  }
  const rgb = text.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?/);
  if (rgb) {
    const raw = rgb[4];
    const alpha = raw === undefined ? 1 : raw.endsWith("%") ? Number(raw.slice(0, -1)) / 100 : Number(raw);
    return [Number(rgb[1]), Number(rgb[2]), Number(rgb[3]), Number.isFinite(alpha) ? alpha : 1];
  }
  return null;
}

/** Rangni fon ustiga qo'yadi — shaffof qatlam yolg'on yorqinlik bermasin. */
export function blend([r, g, b, a]: RGBA, over: RGB): RGB {
  return [
    r * a + over[0] * (1 - a),
    g * a + over[1] * (1 - a),
    b * a + over[2] * (1 - a),
  ];
}

/** Rang yozuvi → `RGB`. O'qib bo'lmasa `null` — CHAQIRUVCHI xato deb
 *  hisoblashi kerak, "o'tdi" deb emas.
 *
 *  `over` berilsa shaffof rang o'sha fon ustida hisoblanadi; berilmasa
 *  shaffoflik TASHLANADI (rang o'zicha olinadi). */
export function parseColor(value: string, over?: RGB): RGB | null {
  const rgba = parseRgba(value);
  if (!rgba) return null;
  if (over && rgba[3] < 1) return blend(rgba, over);
  return [rgba[0], rgba[1], rgba[2]];
}

export function toHex(color: RGB): string {
  return `#${color
    .map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0"))
    .join("")}`;
}

export function luminance(color: RGB): number {
  return (
    0.2126 * srgbLinear(color[0]) +
    0.7152 * srgbLinear(color[1]) +
    0.0722 * srgbLinear(color[2])
  );
}

export function contrast(a: RGB, b: RGB): number {
  const x = luminance(a);
  const y = luminance(b);
  const hi = Math.max(x, y);
  const lo = Math.min(x, y);
  return (hi + 0.05) / (lo + 0.05);
}

/** Eng yomon kontrast — bir rang bir nechta fonga qarshi turganda.
 *
 *  `null` qaytsa ranglardan biri o'qilmadi: bu XATO, "o'tdi" emas. */
export function worstContrast(fg: RGB, backgrounds: RGB[]): number | null {
  if (!backgrounds.length) return null;
  let worst = Number.POSITIVE_INFINITY;
  for (const bg of backgrounds) worst = Math.min(worst, contrast(fg, bg));
  return Number.isFinite(worst) ? worst : null;
}

/* ── HSL ──────────────────────────────────────────────────────────────── */

export function hslToRgb(h: number, s: number, l: number): RGB {
  const hue = ((h % 360) + 360) % 360 / 360;
  const sat = Math.max(0, Math.min(1, s));
  const light = Math.max(0, Math.min(1, l));
  if (sat === 0) {
    const v = light * 255;
    return [v, v, v];
  }
  const q = light < 0.5 ? light * (1 + sat) : light + sat - light * sat;
  const p = 2 * light - q;
  const channel = (t: number) => {
    let x = t;
    if (x < 0) x += 1;
    if (x > 1) x -= 1;
    if (x < 1 / 6) return p + (q - p) * 6 * x;
    if (x < 1 / 2) return q;
    if (x < 2 / 3) return p + (q - p) * (2 / 3 - x) * 6;
    return p;
  };
  return [channel(hue + 1 / 3) * 255, channel(hue) * 255, channel(hue - 1 / 3) * 255];
}

export function rgbToHsl(color: RGB): { h: number; s: number; l: number } {
  const [r, g, b] = color.map((v) => v / 255) as [number, number, number];
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return { h: 0, s: 0, l };
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h: number;
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
  else if (max === g) h = ((b - r) / d + 2) / 6;
  else h = ((r - g) / d + 4) / 6;
  return { h: h * 360, s, l };
}

/* ── Hosil qilish ─────────────────────────────────────────────────────── */

/** Tusni berilgan fonlarga nisbatan AA dan o'tadigan qilib keltiradi (D42).
 *
 *  Foydalanuvchi TUS va TO'YINGANLIK tanlaydi, yorqinlikni tizim
 *  hisoblaydi. Sabab o'lchovda: yorug' fon `L ≤ 0.1733`, qorong'i fon
 *  `L ≥ 0.2160` talab qiladi — bu oraliqlar KESISHMAYDI, ya'ni bitta rang
 *  ikki muhitga sig'maydi. Shu sababli dizayn tizimining o'zi ham har
 *  muhitga alohida accent yozadi.
 *
 *  Yo'nalishni eng yomon fon belgilaydi: u yorug' bo'lsa quyuqlashtiramiz.
 *  Qaytaradi: `null` — hech qanday yorqinlik yetmadi (amalda bo'lmaydi,
 *  lekin jimgina yaroqsiz rang qaytarmaslik uchun ochiq qoldirilgan).
 */
/** HEX → accent `{hue, sat}` (D51).
 *
 *  Sozlagichda erkin rang maydoni uchun. Tizim accent'ni TUS sifatida
 *  saqlaydi (D42), chunki yorqinlik har muhit uchun alohida hisoblanadi —
 *  ya'ni HEX dan faqat tus va to'yinganlik olinadi, yorqinlik tashlanadi.
 *  Bu ataylab: `#0F62FE` ni qorong'i rejimga ko'chirish kerak, aks holda
 *  u yerda o'qilmaydi. */
export function hexToAccent(hex: string): { hue: number; sat: number } | null {
  const rgb = parseColor(hex);
  if (!rgb) return null;
  const { h, s } = rgbToHsl(rgb);
  // ⚠️ `rgbToHsl` to'yinganlikni 0–1 da qaytaradi (`h` esa 0–360 da),
  // accent esa 0–100 kutadi. O'lchandi: konversiyasiz `#0F62FE` → `sat: 1`
  // bo'lib, ko'k o'rniga KULRANG chiqardi.
  return { hue: Math.round(h), sat: Math.round(s * 100) };
}

/** Accent → HEX — maydonni joriy rang bilan to'ldirish uchun.
 *  Yorqinlik sozlagich namunalari bilan bir xil (45 %). */
export function accentToHex(hue: number, sat: number): string {
  return toHex(hslToRgb(hue, sat / 100, 0.45));
}

export function deriveAccent(
  hue: number,
  sat: number,
  backgrounds: RGB[],
  target = AA_TARGET,
): RGB | null {
  if (!backgrounds.length) return null;
  // Eng yorug' fon — quyuqlashtirish kerakmi yoki yoritishmi, shu belgilaydi.
  const lightest = backgrounds.reduce((a, b) => (luminance(a) >= luminance(b) ? a : b));
  const goDarker = luminance(lightest) > 0.5;
  let lo = goDarker ? 0 : 0.5;
  let hi = goDarker ? 0.5 : 1;
  let best: RGB | null = null;
  for (let i = 0; i < 24; i += 1) {
    const mid = (lo + hi) / 2;
    const candidate = hslToRgb(hue, sat, mid);
    const ratio = worstContrast(candidate, backgrounds);
    if (ratio !== null && ratio >= target) {
      best = candidate;
      // Chegaraga eng yaqin (ya'ni tus eng "to'yingan") nuqtani saqlaymiz.
      if (goDarker) lo = mid;
      else hi = mid;
    } else if (goDarker) {
      hi = mid;
    } else {
      lo = mid;
    }
  }
  return best;
}

/** Accent ustidagi matn rangi (D8, D46).
 *
 *  Kafolat **diapazondan** keladi, ink tanlovidan emas: yorug' diapazondagi
 *  accent uchun oq, qorong'i diapazondagi uchun quyuq ink. Toza qora
 *  o'rniga `--rw-ground` ishlatiladi (loyiha an'anasi) — diapazon
 *  krossoverdan qochgani uchun bu xavfsiz.
 */
export function accentInk(accent: RGB, lightInk: RGB, darkInk: RGB): RGB {
  const onLight = contrast(lightInk, accent);
  const onDark = contrast(darkInk, accent);
  return onDark >= onLight ? darkInk : lightInk;
}

/** Accent'ning och/qorong'i nusxasi — chip foni (`.rw-accent-soft`).
 *
 *  `dark` — O'LCHANGAN muhit (`environmentIsDark`), klass emas. */
export function accentSoft(hue: number, sat: number, dark: boolean): RGB {
  return dark ? hslToRgb(hue, Math.min(sat, 0.5), 0.14) : hslToRgb(hue, Math.min(sat, 0.6), 0.95);
}

/* ── DOM o'qish ───────────────────────────────────────────────────────── */

/** Joriy uslubning fon tokeni qiymati. O'qilmasa `null`. */
export function readToken(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

/** `tools/check_contrast.py` dagi `backgrounds()` bilan bir xil ro'yxat.
 *
 *  ⚠️ Qo'lda faqat `ground`/`surface` ni olish yetarli emas: checker
 *  `--rw-hover`, `--rw-chip`, `--rw-field` ni ham fon sifatida oladi va
 *  aynan shu sabab bilan accent nuqsoni 7 palitrada yashiringan edi.
 */
const BACKGROUND_TOKENS = [
  "--rw-ground",
  "--rw-surface",
  "--rw-surface-2",
  "--rw-chrome",
  "--rw-chip",
  "--rw-field",
  "--rw-hover",
] as const;

/** Joriy uslubning o'lchanadigan fonlari. */
export function readBackgrounds(): RGB[] {
  // Ildiz fon BIRINCHI o'qiladi: qolgan sirtlar ko'pincha shaffof
  // (`rgba(0, 0, 0, .62)`) va ular aynan shu fon ustida turadi. Ularni
  // shaffofligicha o'lchash yorqinlikni yolg'on ko'rsatardi — qora
  // 62% qora emas.
  const ground = parseColor(readToken("--rw-ground"));
  const out: RGB[] = ground ? [ground] : [];
  for (const token of BACKGROUND_TOKENS) {
    if (token === "--rw-ground") continue;
    const parsed = parseColor(readToken(token), ground ?? undefined);
    if (parsed) out.push(parsed);
  }
  return out;
}

/** Joriy muhit qorong'imi — O'LCHANGAN fon yorqinligidan.
 *
 *  ⚠️ `<html>` dagi `dark` klassi bu yerda ISHLATILMAYDI: bir muhitli
 *  uslublarda (`dual: false` — `clay`, `terminal`, `aurora`…) u yolg'on
 *  gapiradi. `clay` da `dark` klassi turibdi, lekin uning barcha fonlari
 *  YORUG' (`--rw-ground: #ede4ff`), chunki `[data-style="clay"].dark`
 *  bloki umuman yo'q.
 *
 *  Bu o'lchov bilan topilgan xato edi: klassga qarab chip qorong'i
 *  qilinardi, fonlar esa yorug' qolardi, natijada yorug' va qorong'i
 *  aralash ro'yxat hosil bo'lib, hech qanday ink ikkalasiga ham sig'masdi.
 *  Oqibat: `--rw-accent-ink` accent'ning o'ziga tushib qolardi va havola
 *  matni 2.74:1 bo'lardi.
 */
export function environmentIsDark(backgrounds: RGB[]): boolean {
  const ground = parseColor(readToken("--rw-ground"));
  const base = ground ?? backgrounds[0];
  return base ? luminance(base) < 0.5 : false;
}
