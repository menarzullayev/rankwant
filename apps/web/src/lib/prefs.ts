/** Ko'rinish sozlamalarining qurilmadagi nusxasi.
 *
 * Haqiqat manbai — hisob (`ui_prefs`, `theme`, `locale`): odam boshqa
 * qurilmadan kirsa ham o'z uslubini ko'radi. Lekin mavzu va uslubni
 * hidratsiyadan OLDIN qo'yish kerak (`layout.tsx`), u paytda sessiya
 * hali o'qilmagan — shuning uchun qiymat `localStorage` da ham turadi.
 */

import type {
  A11yPrefs,
  AppearancePrefs,
  ThemeEffect,
  ThemeTemplate,
} from "@/lib/api";

export const PREFS_EVENT = "rw:prefs";

/** Sarlavhadagi tugmalar hisobni bilmaydi (provayderlar sessiyadan
 *  tashqarida) — ular hodisa yuboradi, `PrefsSync` esa uni hisobga yozadi.
 *
 *  `theme` — TANLANGAN rejim (`system` ham bo'lishi mumkin), yechilgan
 *  mavzu emas. Server ham shu qiymatni saqlaydi (`User.theme`). */
export type PrefsChange = {
  theme?: "light" | "dark" | "system";
  style?: string;
  locale?: string;
  /** Sozlagichdan kelgan o'zgarishlar — `PrefsSync` ularni `ui_prefs`
   *  ning `appearance`/`a11y` guruhlariga qo'shadi (D33). */
  appearance?: Partial<AppearancePrefs>;
  a11y?: Partial<A11yPrefs>;
  /** Shaxsiy shablonlar (D21) — butun ro'yxat, bo'lak emas. */
  templates?: ThemeTemplate[];
};

/** Sozlagichning qurilmadagi nusxasi — hidratsiyadan OLDIN qo'llanadi.
 *
 *  Accent bu yerda HISOBLANGAN holda turadi (hex), chunki uni hosil
 *  qilish uchun fon yorqinligini o'lchash kerak, boot skriptda esa DOM
 *  hali tayyor emas. Ya'ni hisob bir marta bajariladi va keshlanadi. */
export const APPEARANCE_KEY = "rw:appearance";
export const A11Y_KEY = "rw:a11y";
export const ACCENT_KEY = "rw:accent";
export const TEMPLATES_KEY = "rw:templates";

export type StoredAccent = {
  accent: string;
  fg: string;
  soft: string;
  ink: string;
};

const SOUND_KEY = "rw:sound";
const EFFECT_KEY = "rw:effect";

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function writeLocal(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Private rejimda yozib bo'lmaydi — sozlama sessiya davomida ishlaydi.
  }
}

export function announcePrefs(change: PrefsChange) {
  window.dispatchEvent(new CustomEvent(PREFS_EVENT, { detail: change }));
}

export function rememberPrefs(prefs: { sound?: boolean; effect?: ThemeEffect }) {
  if (prefs.sound !== undefined) writeLocal(SOUND_KEY, prefs.sound ? "1" : "0");
  if (prefs.effect) writeLocal(EFFECT_KEY, prefs.effect);
}

export function removeLocal(key: string) {
  try {
    localStorage.removeItem(key);
  } catch {
    // Private rejim — yozib ham, o'chirib ham bo'lmaydi.
  }
}

/** Sozlagich tanlovini qurilmaga yozadi (hisobga `PrefsSync` yozadi).
 *
 *  ⚠️ Accent keshiga TEGMAYDI: uni `applyAccent` yozadi, chunki u
 *  hisoblangan qiymatni biladi. Ilgari bu funksiya `null` bilan
 *  chaqirilib keshni o'chirib qo'yardi — natijada accent saqlanmasdi. */
export function rememberAppearance(
  appearance: AppearancePrefs,
  a11y: A11yPrefs,
  templates: ThemeTemplate[] = [],
) {
  writeLocal(APPEARANCE_KEY, JSON.stringify(appearance));
  writeLocal(A11Y_KEY, JSON.stringify(a11y));
  writeLocal(TEMPLATES_KEY, JSON.stringify(templates));
}

/** Accent HISOBLANGAN holda saqlanadi — boot skript uni o'lchovsiz
 *  qo'llay olsin (fon yorqinligini o'sha paytda o'lchab bo'lmaydi). */
export function rememberAccent(accent: (StoredAccent & { style: string }) | null) {
  if (accent) writeLocal(ACCENT_KEY, JSON.stringify(accent));
  else removeLocal(ACCENT_KEY);
}

/** Ovoz standart holatda O'CHIQ: so'ramasdan ovoz chiqaradigan sayt
 *  sinfda yoki kutubxonada ochilganda odamni noqulay holatga soladi. */
export const soundEnabled = () => read(SOUND_KEY) === "1";

export function themeEffect(): ThemeEffect {
  const value = read(EFFECT_KEY);
  return value === "none" || value === "circle" ? value : "fade";
}

let audio: AudioContext | null = null;

/** «Qabul qilindi» ohangi — ikki qisqa nota, fayl yuklamasdan.
 *
 *  Ovoz — bezak: brauzer uni bermasa (avtoijro siyosati, eski brauzer)
 *  hech narsa buzilmasligi kerak, shuning uchun xato yutiladi. */
export function playSuccess({ force = false } = {}) {
  if (!force && !soundEnabled()) return;
  try {
    const Ctor =
      window.AudioContext ??
      (window as unknown as { webkitAudioContext?: typeof AudioContext })
        .webkitAudioContext;
    if (!Ctor) return;
    audio ??= new Ctor();
    const ctx = audio;
    if (ctx.state === "suspended") void ctx.resume();
    const now = ctx.currentTime;
    for (const [freq, at] of [
      [1046.5, 0],
      [1568, 0.09],
    ]) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.0001, now + at);
      gain.gain.exponentialRampToValueAtTime(0.16, now + at + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + at + 0.35);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now + at);
      osc.stop(now + at + 0.4);
    }
  } catch {
    // ovoz chiqmadi — natija baribir ekranda
  }
}
