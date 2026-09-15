/** Ikonka to'plamlari (D10) va qamrov qoidasi (D20 = ①).
 *
 *  ⚠️ **Nega bu fayl `icons/` da emas, `lib/theme/` da**: u SVG
 *  ko'rsatmaydi — u **sozlama** va **qoida**. Komponent emas, ma'lumot.
 *  `apply.ts`, `share.ts`, `prefs.ts` va Customizer hammasi shu yerdan
 *  o'qiydi, ya'ni hech biri `icons/` ga bog'lanmaydi.
 *
 *  ── Qamrov qoidasi (D20 ①) ──────────────────────────────────────────
 *
 *  To'plam almashganda **nav · amallar · holat** o'zgaradi,
 *  **verdikt · brend QAT'IY** qoladi.
 *
 *  Sabab: qo'llanma, yordam sahifalari va video darsliklar verdikt
 *  belgisiga tayanadi — u o'zgarsa hamma foydalanuvchida boshqacha
 *  ko'rinadi. Brend logotiplarini (Telegram, GitHub, Instagram)
 *  o'zgartirish esa brend siyosatini buzardi.
 *
 *  Qoida **kalit nomidan** olinadi (D18: `domen.ob'ekt.holat`), ya'ni
 *  registrga alohida "qat'iy" bayrog'i qo'yish shart emas — nomning
 *  birinchi bo'lagi qaror qiladi. Bu xatoning oldini oladi: yangi kalit
 *  qo'shilsa, u avtomatik to'g'ri guruhga tushadi.
 */

export type IconPackId =
  | "lucide"
  | "phosphor"
  | "phosphorSolid"
  | "phosphorDuotone"
  | "heroicons"
  | "heroiconsSolid"
  | "tabler"
  | "bootstrap"
  | "remix"
  | "simple";

/** Domenlar (D18: `domen.ob'ekt.holat` ning birinchi bo'lagi).
 *
 *  ⚠️ Kalitning birinchi bo'lagi shu ro'yxatdan bo'lishi SHART.
 *  `tools/check_icons.py` buni tekshiradi — notanish domen jimgina o'tib
 *  ketmasin, chunki u qat'iy hisoblanadi va foydalanuvchi kutgan ikonka
 *  almashmay qolardi. */
export type IconZone =
  // Interfeys — to'plamga bo'ysunadi (D20 ①).
  | "nav"
  | "action"
  | "status"
  | "ranking"
  | "user"
  | "contest"
  | "content"
  | "notification"
  | "shop"
  | "markdown"
  | "locale"
  | "stats"
  | "system"
  | "device"
  | "empty"
  | "error"
  | "media"
  // Qat'iy — to'plamga bo'ysunmaydi.
  | "verdict"
  | "brand";

/** Qaysi domen to'plamga bo'ysunadi (D20 ①).
 *
 *  `true`  — ikonka foydalanuvchi tanlagan to'plamdan chiziladi.
 *  `false` — QAT'IY: verdikt va brend.
 *
 *  Sabab: qo'llanma, yordam sahifalari va video darsliklar verdikt
 *  belgisiga tayanadi — u o'zgarsa hamma foydalanuvchida boshqacha
 *  ko'rinadi. Brend logotiplarini (Telegram, GitHub, Python) o'zgartirish
 *  esa brend siyosatini buzardi; ular `lib/tech-icons.tsx` da yashaydi. */
export const ZONES: Record<IconZone, boolean> = {
  nav: true,
  action: true,
  status: true,
  ranking: true,
  user: true,
  contest: true,
  content: true,
  notification: true,
  shop: true,
  markdown: true,
  locale: true,
  stats: true,
  system: true,
  device: true,
  empty: true,
  error: true,
  media: true,
  verdict: false,
  brand: false,
};

/** To'plamga bo'ysunmaydigan domenlar — tekshiruv va hujjat uchun. */
export const FIXED_ZONES: IconZone[] = (Object.keys(ZONES) as IconZone[]).filter(
  (z) => !ZONES[z]
);

/** Standart to'plam (D11). Lucide — eng keng tarqalgan va eng neytral. */
export const DEFAULT_ICON_PACK: IconPackId = "lucide";

export type IconPack = {
  id: IconPackId;
  /** Brend nomi — tarjima QILINMAYDI (atoqli nom). */
  name: string;
  /** Uslub: `outline` · `solid` · `duotone`. */
  style: "outline" | "solid" | "duotone";
  /** Chizim o'lchami (D3: 16/20/24/32 px shkalasi uchun mo'ljallangan). */
  grid: number;
  /** Manba paketi — qayta generatsiya uchun. */
  source: string;
  license: string;
  /** Nur (stroke) qalinligi — outline to'plamlari uchun. */
  stroke?: number;
  /** Interfeys ikonkalari bormi.
   *
   *  ⚠️ Simple Icons — **faqat brend** to'plami: uning ichida `search`
   *  yoki `settings` yo'q, faqat kompaniya logotiplari. Uni interfeys
   *  to'plami sifatida tanlash imkonsiz, chunki D20 ① da brend
   *  **qat'iy** — ya'ni tanlov hech narsani o'zgartirmasdi.
   *
   *  Shuning uchun u ro'yxatda qoladi (D10 shunday degan), lekin
   *  tanlov ekranida ko'rinmaydi. */
  interface: boolean;
};

/** O'nta to'plam (D10). Tartib — tanlov ekranidagi tartib. */
export const ICON_PACKS: IconPack[] = [
  {
    id: "lucide",
    interface: true,
    name: "Lucide",
    style: "outline",
    grid: 24,
    source: "lucide-static",
    license: "ISC",
    stroke: 2,
  },
  {
    id: "phosphor",
    interface: true,
    name: "Phosphor",
    style: "outline",
    grid: 256,
    source: "@phosphor-icons/core (regular)",
    license: "MIT",
    stroke: 16,
  },
  {
    id: "phosphorSolid",
    interface: true,
    name: "Phosphor Solid",
    style: "solid",
    grid: 256,
    source: "@phosphor-icons/core (fill)",
    license: "MIT",
  },
  {
    id: "phosphorDuotone",
    interface: true,
    name: "Phosphor Duotone",
    style: "duotone",
    grid: 256,
    source: "@phosphor-icons/core (duotone)",
    license: "MIT",
  },
  {
    id: "heroicons",
    interface: true,
    name: "Heroicons",
    style: "outline",
    grid: 24,
    source: "heroicons (24/outline)",
    license: "MIT",
    stroke: 1.5,
  },
  {
    id: "heroiconsSolid",
    interface: true,
    name: "Heroicons Solid",
    style: "solid",
    grid: 24,
    source: "heroicons (24/solid)",
    license: "MIT",
  },
  {
    id: "tabler",
    interface: true,
    name: "Tabler",
    style: "outline",
    grid: 24,
    source: "@tabler/icons (outline)",
    license: "MIT",
    stroke: 2,
  },
  {
    id: "bootstrap",
    interface: true,
    name: "Bootstrap Icons",
    style: "solid",
    grid: 16,
    source: "bootstrap-icons",
    license: "MIT",
  },
  {
    id: "remix",
    interface: true,
    name: "Remix Icon",
    style: "outline",
    grid: 24,
    source: "remixicon (line)",
    license: "Apache-2.0",
    stroke: 1.6,
  },
  {
    id: "simple",
    interface: false,
    name: "Simple Icons",
    style: "solid",
    grid: 24,
    source: "simple-icons",
    license: "CC0-1.0",
  },
];

/** ⚠️ Faqat **interfeys** to'plamlari qabul qilinadi. Simple Icons ni
 *  tanlash `DEFAULT_ICON_PACK` ga qaytaradi — ya'ni hech narsa
 *  o'zgarmaydi, lekin sozlama ham buzilmaydi. */
export function clampIconPack(value: unknown): IconPackId {
  return ICON_PACKS.some((p) => p.id === value && p.interface)
    ? (value as IconPackId)
    : DEFAULT_ICON_PACK;
}

/** Tanlov ekranida ko'rinadigan to'plamlar. */
export const SELECTABLE_PACKS = ICON_PACKS.filter((p) => p.interface);

export function iconPack(id: IconPackId): IconPack {
  return ICON_PACKS.find((p) => p.id === id) ?? ICON_PACKS[0];
}

/** Kalitning domeni (`nav.problems` → `nav`). Notanish bo'lsa `null`. */
export function zoneOf(key: string): IconZone | null {
  const head = key.split(".")[0];
  return head in ZONES ? (head as IconZone) : null;
}

/** Shu kalit to'plam almashganda o'zgaradimi (D20 ①).
 *
 *  ⚠️ Notanish domen **`false`** qaytaradi — ya'ni qat'iy hisoblanadi.
 *  Ataylab: yangi kalit qo'shilib domeni xato yozilsa, u jimgina
 *  almashavermaydi, balki `check_icons.py` da xato bo'lib chiqadi.
 */
export function changesWithPack(key: string): boolean {
  const z = zoneOf(key);
  return z ? ZONES[z] : false;
}
