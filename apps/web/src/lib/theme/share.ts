/** Shablonni havola orqali ulashish (D22).
 *
 *  Sozlamalar URL parametrlariga yoziladi — moderatsiya ham, saqlash joyi
 *  ham kerak emas. Umumiy kutubxona (D22 da rad etilgan) spam va kontrast
 *  nazoratini talab qilardi; havola o'sha ehtiyojning ko'p qismini
 *  arzon qondiradi.
 *
 *  Havolani olgan odam ko'rinishni **ko'radi** va xohlasa shablon qilib
 *  saqlaydi. Parametrlar o'qilgach manzildan olib tashlanadi
 *  (`history.replaceState`) — aks holda har yuklanishda qayta qo'llanib,
 *  odam o'z sozlamasini o'zgartira olmay qolardi.
 */

import type { AppearancePrefs } from "@/lib/api";

const KEYS = ["style", "accent", "font", "size", "density"] as const;

/** Ko'rinishni URL ga yozadi. Bo'sh joylar tushib qoladi — havola qisqa
 *  bo'lsin va faqat o'zgartirilgan narsa ko'rinsin. */
export function encodeAppearance(appearance: AppearancePrefs): string {
  const params = new URLSearchParams();
  if (appearance.style) params.set("style", appearance.style);
  if (appearance.accent) {
    params.set("accent", `${appearance.accent.hue}-${appearance.accent.sat}`);
  }
  if (appearance.font) params.set("font", appearance.font);
  if (appearance.size && appearance.size !== 100) {
    params.set("size", String(appearance.size));
  }
  if (appearance.density && appearance.density !== "comfortable") {
    params.set("density", appearance.density);
  }
  return params.toString();
}

/** URL dan ko'rinishni o'qiydi. Hech narsa yo'q bo'lsa — `null`.
 *
 *  Notanish qiymatlar JIMGINA tashlab yuboriladi: begona havola butun
 *  ko'rinishni buzmasligi kerak, lekin uni qo'llash ham mumkin emas.
 */
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
  if (font && ["inter", "jakarta", "roboto", "dm-sans"].includes(font)) {
    out.font = font;
  }

  const size = Number(params.get("size"));
  if ([90, 100, 110, 120].includes(size)) out.size = size;

  const density = params.get("density");
  if (density && ["compact", "comfortable", "spacious"].includes(density)) {
    out.density = density as AppearancePrefs["density"];
  }

  return Object.keys(out).length ? out : null;
}

/** Joriy manzilga ko'rinish parametrlarini qo'shib qaytaradi. */
export function shareUrl(appearance: AppearancePrefs): string {
  const url = new URL(window.location.href);
  for (const key of KEYS) url.searchParams.delete(key);
  const encoded = encodeAppearance(appearance);
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
