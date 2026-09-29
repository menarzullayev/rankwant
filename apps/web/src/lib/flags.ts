/** Feature flag reyestri — bitta joyda ro'yxatga olingan bayroqlar.
 *
 *  ## Nega reyestr, erkin `process.env` emas
 *
 *  Ilgari faqat bitta "bayroq" bor edi: `experiments.ts` dagi
 *  `GEO_EXPERIMENT` — u A/B guruhni cookie'dan o'qirdi. Yangi bayroq
 *  qo'shish uchun yangi fayl, yangi cookie o'qish, yangi parse qilish
 *  kerak bo'lardi. Bayroq soni o'sganda bu takror kodga aylanadi va eng
 *  yomoni — **har biri boshqacha yo'l bilan o'chiriladi**, ya'ni
 *  «o'chirib qo'yish» degan bitta amal bo'lmaydi.
 *
 *  Bu reyestr uchta savolga bitta javob beradi:
 *
 *  1. **Qaysi bayroqlar bor?** — `FLAGS` obyekti (yagona ro'yxat).
 *  2. **Kimda yoniq?** — `isOn()`: eksperiment → muhit → standart.
 *  3. **Qanday o'chiriladi?** — `FLAG_OVERRIDES` cookie (faqat dev) yoki
 *     `NEXT_PUBLIC_FLAG_<NOM>` muhit o'zgaruvchisi.
 *
 *  ## Uch qavat (tartib muhim)
 *
 *  | Qavat                | Kim ishlatadi      | Misol                        |
 *  |----------------------|--------------------|------------------------------|
 *  | `FLAGS` (kod)        | manba              | standart qiymat, izoh        |
 *  | `NEXT_PUBLIC_FLAG_*` | deploy/ops         | `NEXT_PUBLIC_FLAG_NEW_NAV=1` |
 *  | `FLAG_OVERRIDES`     | ishlab chiqish     | brauzer cookie'si            |
 *
 *  ⚠️ **Server va mijoz bir xil javob berishi kerak.** Shu sababli qiymat
 *  `NEXT_PUBLIC_` prefiksli o'zgaruvchidan o'qiladi: u build paytida
 *  **ikkala to'plamga** ham singdiriladi. Prefikssiz o'zgaruvchi faqat
 *  serverda ko'rinardi va sahifa serverda `true`, brauzerda `false`
 *  chizib **hidratsiya xatosi** berardi.
 *
 *  ⚠️ **Override faqat dev.** `FLAG_OVERRIDES` cookie'si ishlab
 *  chiqarishda **o'qilmaydi**: aks holda har qanday foydalanuvchi
 *  konsolda cookie qo'yib yoqilmagan funksiyani ochib olardi. Bu
 *  qulaylik, xavfsizlik emas — lekin yopilgan eshik ochiq qolmasligi
 *  kerak.
 *
 *  ```ts
 *  import { isOn, isOnServer } from "@/lib/flags";
 *  if (isOn("newNav")) { … }                          // mijoz
 *  isOnServer("newNav", req.headers.get("cookie"))    // server / middleware
 *  ```
 */

const isDev = process.env.NODE_ENV !== "production";

/** Barcha bayroqlar — **yagona ro'yxat**. Yangi bayroq shu yerga
 *  qo'shiladi, boshqa hech qayerda ro'yxat yo'q. */
export const FLAGS = {
  /** Viloyatni ro'yxatdan o'tishning o'zida so'rash (8-qaror A/B).
   *
   *  Bu bayroq cookie'dan emas, eksperiment guruhidan keladi —
   *  quyida `EXPERIMENT_FLAGS` ga qarang. */
  geoEarlyRegion: false,
  /** Yangi navigatsiya qobig'i — ishlab chiqilmoqda. */
  newNav: false,
  /** Qorong'i rejim uchun yangi palitra — sinov. */
  newPalette: false,
  /** Saqlashda optimistik yangilash (server javobini kutmaslik). */
  optimisticSave: false,
} as const;

export type FlagName = keyof typeof FLAGS;

/** Bayroq → eksperiment nomi. Bu yerdagilar `FLAGS` standart qiymatidan
 *  EMAS, balki `rw_exp` cookie'sidagi guruhdan o'qiladi (`b` = yoniq). */
const EXPERIMENT_FLAGS: Partial<Record<FlagName, string>> = {
  geoEarlyRegion: "geo",
};

/** Eksperiment cookie'si — server `proxy.ts` da bir marta qo'yadi. */
export const EXP_COOKIE = "rw_exp";

/** Ishlab chiqish override'i — comma bilan ajratilgan nomlar.
 *  `newNav,optimisticSave` deb qo'yilsa ikkisi yonadi; `!newNav` o'chiradi. */
export const FLAG_OVERRIDES = "rw_flags";

/** `NEXT_PUBLIC_FLAG_<SNAKE_CASE>` muhit o'zgaruvchisini o'qiydi.
 *
 *  ⚠️ `NEXT_PUBLIC_` ni **statik** yozish shart: Next uni faqat
 *  `process.env.NEXT_PUBLIC_X` ko'rinishida ko'rsa almashtiradi.
 *  Dinamik kalit (`process.env[key]`) build paytida topilmaydi va
 *  mijozda `undefined` bo'lib qoladi. Shuning uchun har bir bayroq
 *  alohida satrda sanab chiqiladi. */
function fromEnv(name: FlagName): boolean | undefined {
  let raw: string | undefined;
  switch (name) {
    case "geoEarlyRegion":
      raw = process.env.NEXT_PUBLIC_FLAG_GEO_EARLY_REGION;
      break;
    case "newNav":
      raw = process.env.NEXT_PUBLIC_FLAG_NEW_NAV;
      break;
    case "newPalette":
      raw = process.env.NEXT_PUBLIC_FLAG_NEW_PALETTE;
      break;
    case "optimisticSave":
      raw = process.env.NEXT_PUBLIC_FLAG_OPTIMISTIC_SAVE;
      break;
  }
  if (raw === undefined || raw === "") return undefined;
  return raw === "1" || raw.toLowerCase() === "true";
}

/** Cookie'dagi qiymatni o'qiydi — sof, shartsiz. */
function cookieValue(name: string): string | undefined {
  if (typeof document === "undefined") return undefined;
  const raw = document.cookie.match(
    new RegExp(`(?:^|;\\s*)${name}=([^;]+)`),
  )?.[1];
  return raw ? decodeURIComponent(raw) : undefined;
}

/** Guruhni cookie matnidan ajratadi — `geo:b,other:a` → `b`.
 *
 *  Bu `experiments.ts` dan ko'chirilgan sof funksiya: uni testlar
 *  allaqachon qoplaydi, mantiq esa o'zgarmagan. */
export function parseVariant(raw: string | undefined, name: string): "a" | "b" {
  if (!raw) return "a";
  for (const part of raw.split(",")) {
    const [key, value] = part.split(":");
    if (key === name && (value === "a" || value === "b")) return value;
  }
  return "a";
}

/** Bayroq yoniqmi — shartsiz, server va mijozda bir xil.
 *
 *  Tartib:
 *  1. Dev override cookie (`rw_flags`) — faqat ishlab chiqishda.
 *  2. Eksperiment guruhi (`rw_exp`) — agar bayroq eksperimentga bog'langan.
 *  3. Muhit o'zgaruvchisi — `NEXT_PUBLIC_FLAG_*`.
 *  4. `FLAGS` standarti.
 */
export function isOn(name: FlagName): boolean {
  if (isDev) {
    const override = cookieValue(FLAG_OVERRIDES);
    if (override !== undefined) {
      const list = override.split(",").map((s) => s.trim()).filter(Boolean);
      // `!nom` — majburan o'chirish (masalan `!newNav`).
      if (list.includes(`!${name}`)) return false;
      if (list.includes(name)) return true;
    }
  }

  const experiment = EXPERIMENT_FLAGS[name];
  if (experiment) {
    return parseVariant(cookieValue(EXP_COOKIE), experiment) === "b";
  }

  const env = fromEnv(name);
  if (env !== undefined) return env;

  return FLAGS[name];
}

/** Bayroqni server tomonda `Cookie` sarlavhasidan o'qiydi.
 *
 *  ⚠️ Mijozdagi `document.cookie` server komponentida yo'q, ya'ni
 *  `isOn` u yerda har doim standartni qaytarardi va SSR/mijoz
 *  nomuvofiqligi chiqardi. Server komponentlar shu funksiyani
 *  ishlatishi kerak.
 *
 *  ⚠️ **`react` import qilinmaydi.** Ilgari bu faylda `useFlag` hook
 *  ham bor edi va u `react` ni tortardi; `middleware` (`proxy.ts`) va
 *  Edge runtime React hook'ni ko'tarmaydi, ya'ni `next build`
 *  «Ecmascript file had an error» bilan yiqilardi (o'lchandi
 *  2026-09-24). Bu fayl endi **sof** — React'siz, Edge'da ham
 *  ishlaydi. `isOn` sof funksiya bo'lgani uchun hook kerak emas:
 *  bayroq qiymati render paytida o'zgarmaydi (cookie build/deploy bilan
 *  keladi), ya'ni `useState` faqat keraksiz qatlam qo'shardi. */
export function isOnServer(name: FlagName, cookieHeader: string | undefined): boolean {
  const experiment = EXPERIMENT_FLAGS[name];
  if (experiment) {
    const match = cookieHeader?.match(
      new RegExp(`(?:^|;\\s*)${EXP_COOKIE}=([^;]+)`),
    )?.[1];
    return parseVariant(match ? decodeURIComponent(match) : undefined, experiment) === "b";
  }
  return fromEnv(name) ?? FLAGS[name];
}
