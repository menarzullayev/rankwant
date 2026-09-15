/** Judge verdiktlari — yagona ma'lumot manbasi (D56).
 *
 *  Nega alohida fayl: verdikt platformada **uch joyda** ko'rinadi — urinishlar
 *  jadvali, masala sahifasi va reyting. Ilgari har biri o'z rangini qo'lda
 *  yozardi, ya'ni "Accepted" bir joyda yashil, boshqasida boshqa yashil
 *  bo'lishi mumkin edi.
 *
 *  Bu fayl nom, rang va ikonka kalitini bir joyda saqlaydi; ko'rinish esa
 *  `Verdict` komponentida (5 xil variant).
 *
 *  ⚠️ Ranglar WCAG AA (4.5:1) bo'yicha tanlangan — oq fon ustida ham,
 *  `-soft` fon ustida ham o'qiladi. O'zgartirsang, `check_contrast.py` ni
 *  ishga tushir.
 */

/** Verdikt kaliti — API shu qiymatlarni qaytaradi. */
export type VerdictKey =
  | "AC"
  | "WA"
  | "TLE"
  | "MLE"
  | "RE"
  | "CE"
  | "PE"
  | "OLE"
  | "IE"
  | "PD";

export type VerdictDef = {
  /** Qisqa kod — jadvalda ko'rinadi. */
  key: VerdictKey;
  /** Ikonka kaliti (`icons/keys.ts` dan). */
  icon: string;
  /** Matn rangi — `-soft` fon ustida ham, oq fonda ham AA dan o'tadi. */
  color: string;
  /** Fon rangi — ① nishon va ⑤ doira uchun. */
  background: string;
  /** To'liq nomi — ④ va ⑩ uchun. Tarjima qilinmaydi (xalqaro atama). */
  label: string;
  /** Qisqa izoh — ⑩ kartada. i18n kaliti. */
  hintKey: string;
};

export const VERDICTS: Record<VerdictKey, VerdictDef> = {
  AC: {
    key: "AC",
    icon: "check-circle",
    color: "#0a6b3d",
    background: "#e6f7ee",
    label: "Accepted",
    hintKey: "verdict.hint.AC",
  },
  WA: {
    key: "WA",
    icon: "x-circle",
    color: "#a32020",
    background: "#fdeaea",
    label: "Wrong Answer",
    hintKey: "verdict.hint.WA",
  },
  TLE: {
    key: "TLE",
    icon: "timer",
    color: "#8a5a00",
    background: "#fff8e6",
    label: "Time Limit Exceeded",
    hintKey: "verdict.hint.TLE",
  },
  MLE: {
    key: "MLE",
    icon: "cpu",
    color: "#5b3fa8",
    background: "#f0ecfb",
    label: "Memory Limit Exceeded",
    hintKey: "verdict.hint.MLE",
  },
  RE: {
    key: "RE",
    icon: "warning-octagon",
    color: "#b45309",
    background: "#fef3e2",
    label: "Runtime Error",
    hintKey: "verdict.hint.RE",
  },
  CE: {
    key: "CE",
    icon: "wrench",
    color: "#4b5563",
    background: "#f1f3f5",
    label: "Compilation Error",
    hintKey: "verdict.hint.CE",
  },
  PE: {
    key: "PE",
    icon: "ruler",
    color: "#0e7490",
    background: "#e6f6fa",
    label: "Presentation Error",
    hintKey: "verdict.hint.PE",
  },
  OLE: {
    key: "OLE",
    icon: "upload-simple",
    color: "#a21caf",
    background: "#fbeefb",
    label: "Output Limit Exceeded",
    hintKey: "verdict.hint.OLE",
  },
  IE: {
    key: "IE",
    icon: "gear",
    color: "#78350f",
    background: "#f5efe6",
    label: "Internal Error",
    hintKey: "verdict.hint.IE",
  },
  PD: {
    key: "PD",
    icon: "hourglass",
    color: "#5b6472",
    background: "#f1f3f5",
    label: "Pending",
    hintKey: "verdict.hint.PD",
  },
};

/** Noto'g'ri kalit kelsa — `PD` ga tushadi (jimgina yo'qolmasin). */
export function verdictOf(key: string | undefined | null): VerdictDef {
  const k = String(key ?? "").toUpperCase() as VerdictKey;
  return VERDICTS[k] ?? VERDICTS.PD;
}

/** 10 xil ko'rinish (D57/D59).
 *
 *  Hammasi **bir xil ma'lumotdan** oziqlanadi — farq batafsil darajasida:
 *
 *  | # | id        | Nima ko'rsatadi              |
 *  |---|-----------|------------------------------|
 *  | ① | `badge`   | rangli nishon + kod          |
 *  | ② | `plain`   | faqat ikonka (rangsiz)       |
 *  | ③ | `icon`    | ikonka + kod                 |
 *  | ④ | `full`    | ikonka + to'liq nom          |
 *  | ⑤ | `circle`  | to'ldirilgan doira           |
 *  | ⑥ | `dot`     | rangli nuqta + kod           |
 *  | ⑦ | `box`     | chegara + ikonka             |
 *  | ⑧ | `bar`     | chap chiziq + ikonka + nom   |
 *  | ⑨ | `percent` | ikonka + kod + foiz          |
 *  | ⑩ | `card`    | katta ikonka + nom + izoh    |
 *
 *  `auto` — alohida: ekranga qarab `circle` → `icon` → `full`.
 */
export type VerdictVariant =
  | "auto"
  | "badge"
  | "plain"
  | "icon"
  | "full"
  | "circle"
  | "dot"
  | "box"
  | "bar"
  | "percent"
  | "card";

export const VERDICT_VARIANTS: {
  id: VerdictVariant;
  labelKey: string;
  hintKey: string;
}[] = [
  { id: "auto", labelKey: "verdict.style.auto", hintKey: "verdict.style.autoHint" },
  { id: "badge", labelKey: "verdict.style.badge", hintKey: "verdict.style.badgeHint" },
  { id: "plain", labelKey: "verdict.style.plain", hintKey: "verdict.style.plainHint" },
  { id: "icon", labelKey: "verdict.style.icon", hintKey: "verdict.style.iconHint" },
  { id: "full", labelKey: "verdict.style.full", hintKey: "verdict.style.fullHint" },
  { id: "circle", labelKey: "verdict.style.circle", hintKey: "verdict.style.circleHint" },
  { id: "dot", labelKey: "verdict.style.dot", hintKey: "verdict.style.dotHint" },
  { id: "box", labelKey: "verdict.style.box", hintKey: "verdict.style.boxHint" },
  { id: "bar", labelKey: "verdict.style.bar", hintKey: "verdict.style.barHint" },
  { id: "percent", labelKey: "verdict.style.percent", hintKey: "verdict.style.percentHint" },
  { id: "card", labelKey: "verdict.style.card", hintKey: "verdict.style.cardHint" },
];

export const DEFAULT_VERDICT_VARIANT: VerdictVariant = "auto";

export function clampVerdictVariant(value: unknown): VerdictVariant {
  return VERDICT_VARIANTS.some((v) => v.id === value)
    ? (value as VerdictVariant)
    : DEFAULT_VERDICT_VARIANT;
}
