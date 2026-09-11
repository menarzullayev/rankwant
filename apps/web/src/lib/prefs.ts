/** Ko'rinish sozlamalarining qurilmadagi nusxasi.
 *
 * Haqiqat manbai — hisob (`ui_prefs`, `theme`, `locale`): odam boshqa
 * qurilmadan kirsa ham o'z uslubini ko'radi. Lekin mavzu va uslubni
 * hidratsiyadan OLDIN qo'yish kerak (`layout.tsx`), u paytda sessiya
 * hali o'qilmagan — shuning uchun qiymat `localStorage` da ham turadi.
 */

import type { ThemeEffect } from "@/lib/api";

export const PREFS_EVENT = "rw:prefs";

/** Sarlavhadagi tugmalar hisobni bilmaydi (provayderlar sessiyadan
 *  tashqarida) — ular hodisa yuboradi, `PrefsSync` esa uni hisobga yozadi. */
export type PrefsChange = {
  theme?: "light" | "dark";
  style?: string;
  locale?: string;
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
