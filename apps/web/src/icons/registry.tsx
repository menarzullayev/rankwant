"use client";

import { useSyncExternalStore } from "react";

import { DEFAULT_ICON_PACK, type IconPackId } from "@/lib/theme/icon-packs";
import { LUCIDE_ICONS } from "./packs/lucide";

/** Semantik kalit → ikonka (D4, D18).
 *
 *  Kod **kalitni** biladi, to'plamni emas: `icon("nav.problems")`. Qaysi
 *  glif chizilishini foydalanuvchi tanlovi hal qiladi.
 *
 *  ── Nega dinamik yuklash (D17) ───────────────────────────────────────
 *
 *  O'lchandi: hozir 44 kalit × 6 to'plam = **30 KB gzip** (bittasi
 *  3.5–8.4 KB). Ya'ni subset yondashuvi D17 hal qilmoqchi bo'lgan muammoni
 *  allaqachon yechgan — 2200 ikonkani butunlay yuklash haqida gap yo'q.
 *
 *  Lekin kalitlar soni ~220 ga o'sganda (V3) olti to'plam ~150 KB bo'ladi,
 *  ya'ni dinamik yuklash **o'sha paytda** o'zini oqlaydi. Shuning uchun
 *  mexanizm hozirdan qurilgan: standart to'plam (Lucide) asosiy bundle'da
 *  qoladi, qolgani alohida bo'lak bo'lib yuklanadi.
 *
 *  ── Nega `useSyncExternalStore` ──────────────────────────────────────
 *
 *  Loyihada effektda `setState` taqiqlangan (`react-hooks/set-state-in-effect`):
 *  u kaskad render keltiradi. `useSyncExternalStore` esa tashqi holatni
 *  o'qishning rasmiy yo'li — va muhimi, **server snapshot** beriladi, ya'ni
 *  hidratsiya buzilmaydi: server ham, klientning birinchi renderi ham
 *  standart to'plamni chizadi, keyin yuklangan to'plam keladi.
 *
 *  ⚠️ Shu sababli standart bo'lmagan to'plam tanlagan foydalanuvchi
 *  **bir marta** almashishni ko'radi (sessiyada bir marta — modul keshi
 *  saqlaydi). Bu ataylab: muqobil — barcha 6 to'plamni boshidan yuklash,
 *  ya'ni har bir foydalanuvchiga 30 KB, holbuki u bittasini ishlatadi.
 */

type IconFn = (p: { className?: string }) => React.JSX.Element;
type IconMap = Record<string, IconFn>;

/** Standart to'plam — asosiy bundle ichida (D17). */
const STATIC_PACKS: Partial<Record<IconPackId, IconMap>> = {
  lucide: LUCIDE_ICONS,
};

/** Qolgani — alohida bo'lak. `import()` Next'ning bo'laklashini beradi. */
const LOADERS: Record<IconPackId, () => Promise<IconMap>> = {
  lucide: () => Promise.resolve(LUCIDE_ICONS),
  tabler: () => import("./packs/tabler").then((m) => m.TABLER_ICONS),
  heroicons: () => import("./packs/heroicons").then((m) => m.HEROICONS_ICONS),
  heroiconsSolid: () =>
    import("./packs/heroiconsSolid").then((m) => m.HEROICONSSOLID_ICONS),
  bootstrap: () => import("./packs/bootstrap").then((m) => m.BOOTSTRAP_ICONS),
  remix: () => import("./packs/remix").then((m) => m.REMIX_ICONS),
  // Phosphor allaqachon yuklangan (`phosphor.tsx`) — u verdikt va brend
  // uchun qat'iy ishlatiladi (D20 ①), ya'ni bu yerga faqat interfeys
  // kalitlari uchun kerak bo'ladi.
  phosphor: () => import("./packs/phosphorRegular").then((m) => m.PHOSPHOR_ICONS),
  phosphorSolid: () => import("./packs/phosphorSolid").then((m) => m.PHOSPHORSOLID_ICONS),
  phosphorDuotone: () =>
    import("./packs/phosphorDuotone").then((m) => m.PHOSPHORDUOTONE_ICONS),
  // ⚠️ Simple Icons — faqat brend to'plami (`interface: false`),
  // ya'ni interfeys ikonkasi yo'q. `clampIconPack` uni hech qachon
  // qaytarmaydi; bu yozuv tip to'liqligi uchun.
  simple: () => Promise.resolve(LUCIDE_ICONS),
};

const loaded = new Map<IconPackId, IconMap>();
const started = new Map<IconPackId, Promise<void>>();
const listeners = new Map<IconPackId, Set<() => void>>();

// Standart to'plam allaqachon qo'lda — uni «yuklash» kerak emas, aks holda
// har bir sahifa bir mikrotask kutib, keraksiz almashish ko'rsatardi.
for (const [id, map] of Object.entries(STATIC_PACKS)) {
  if (map) loaded.set(id as IconPackId, map);
}

function notify(pack: IconPackId) {
  listeners.get(pack)?.forEach((cb) => cb());
}

function start(pack: IconPackId) {
  if (loaded.has(pack) || started.has(pack)) return;
  const p = (LOADERS[pack]?.() ?? LOADERS[DEFAULT_ICON_PACK]())
    .then((map) => {
      loaded.set(pack, map);
      notify(pack);
    })
    .catch(() => {
      // Yuklanmadi — standart to'plam chizilaveradi. Xato ko'rsatishning
      // hojati yo'q: ikonka bezak, sahifa ishlashda davom etadi.
      loaded.set(pack, STATIC_PACKS[DEFAULT_ICON_PACK] ?? {});
      notify(pack);
    });
  started.set(pack, p);
}

function subscribe(pack: IconPackId, cb: () => void) {
  start(pack);
  if (!listeners.has(pack)) listeners.set(pack, new Set());
  listeners.get(pack)!.add(cb);
  return () => listeners.get(pack)?.delete(cb);
}

const getSnapshot = (pack: IconPackId) => loaded.get(pack) ?? null;
/** Server va klientning birinchi renderi — standart to'plam. */
const getServerSnapshot = () => null;

/** Yuklangan to'plam xaritasi, yoki `null` (hali yuklanmagan).
 *
 *  `null` — xato emas: chaqiruvchi standart to'plamga tushadi. */
export function usePackMap(pack: IconPackId): IconMap | null {
  return useSyncExternalStore(
    (cb) => subscribe(pack, cb),
    () => getSnapshot(pack),
    getServerSnapshot
  );
}

/** Ikonkani sinxron olish — yuklangan bo'lsa. Yuklanmagan bo'lsa
 *  standart to'plamdan qaytaradi (ya'ni hech qachon `null` emas, agar
 *  kalit mavjud bo'lsa). */
export function resolveIcon(
  key: string,
  pack: IconPackId,
  map: IconMap | null
): IconFn | null {
  const chosen = map ?? STATIC_PACKS[DEFAULT_ICON_PACK] ?? null;
  return chosen?.[key] ?? STATIC_PACKS[DEFAULT_ICON_PACK]?.[key] ?? null;
}

/** Testlar va `check_icons.py` uchun: qaysi to'plamlar dinamik. */
/** Barcha semantik kalitlar — Customizer galereyasi va tekshiruv uchun.
 *
 *  Kalitlar ro'yxati **standart to'plamdan** olinadi: D12 bo'yicha har bir
 *  to'plam bir xil kalitlarga ega, ya'ni bittasidan olish yetarli.
 *  `tools/check_icons.py` bu tenglikni tekshiradi.
 *
 *  ⚠️ Bu ro'yxat asosiy bundle'ga qo'shiladi (LUCIDE_ICONS allaqachon
 *  statik). Galereya ochilganda qo'shimcha yuklanish bo'lmaydi.
 */
export const ICON_KEYS: string[] = Object.keys(LUCIDE_ICONS).sort();

/** Kalitlarni domen bo'yicha guruhlash — galereya sarlavhalari uchun. */
export function groupKeysByDomain(): [string, string[]][] {
  const by = new Map<string, string[]>();
  for (const k of ICON_KEYS) {
    const domain = k.split(".")[0];
    const list = by.get(domain);
    if (list) list.push(k);
    else by.set(domain, [k]);
  }
  return [...by.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

export const DYNAMIC_PACKS: IconPackId[] = (Object.keys(LOADERS) as IconPackId[]).filter(
  (p) => !STATIC_PACKS[p]
);
