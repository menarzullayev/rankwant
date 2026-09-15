/** Interfeys holati — muvaffaqiyat, ogohlantirish, xato, ma'lumot (D60).
 *
 *  ⚠️ Nega verdiktlardan **alohida** fayl: bular boshqa narsa.
 *
 *  | | Nima haqida | Manba |
 *  |---|---|---|
 *  | `verdict.ts` | Judge natijasi — yechim qabul qilindimi | `apps/api/judging/verdicts.py` |
 *  | `status.ts`  | Interfeys holati — amal bajarildimi | UI hodisalari |
 *
 *  Ikkalasi bitta faylga qo'shilsa, «Accepted» yashili bilan «saqlandi»
 *  yashili bir xil bo'lib qolardi va foydalanuvchi ularni ajratolmasdi.
 *  Ranglar ataylab mos: yashil — yaxshi, sariq — ehtiyot, qizil — yomon.
 *
 *  ⚠️ Ranglar WCAG AA (4.5:1) dan o'tadi. O'zgartirsang,
 *  `python tools/check_contrast.py` ni ishga tushir.
 */

/** To'rt holat — boshqa yo'q. Beshinchisi kerak bo'lsa, avval o'ylang:
 *  holat ko'paygani sari foydalanuvchi ularni ajratmay qo'yadi. */
export type StatusKey = "ok" | "warn" | "bad" | "info";

export type StatusDef = {
  key: StatusKey;
  /** Matn rangi — `soft` fon ustida ham, oq fonda ham AA dan o'tadi. */
  color: string;
  /** Yumshoq fon — nishon, doira va karta uchun. */
  soft: string;
  /** To'liq nom — i18n kaliti (`status.<KALIT>`), 10 tilda mavjud. */
  labelKey: string;
  /** Bir qatorli izoh — i18n kaliti. */
  hintKey: string;
};

export const STATUSES: Record<StatusKey, StatusDef> = {
  ok: {
    key: "ok",
    color: "#0a6b3d",
    soft: "#e6f7ee",
    labelKey: "status.ok",
    hintKey: "status.hint.ok",
  },
  warn: {
    key: "warn",
    color: "#8a5a00",
    soft: "#fff8e6",
    labelKey: "status.warn",
    hintKey: "status.hint.warn",
  },
  bad: {
    key: "bad",
    color: "#a32020",
    soft: "#fdeaea",
    labelKey: "status.bad",
    hintKey: "status.hint.bad",
  },
  info: {
    key: "info",
    color: "#0e7490",
    soft: "#e6f6fa",
    labelKey: "status.info",
    hintKey: "status.hint.info",
  },
};

const KEYS = Object.keys(STATUSES) as StatusKey[];

/** Notanish kalit — `info` ga tushadi. Bu yerda jim yashirish mumkin,
 *  chunki holat **bizning** kodimizdan keladi (verdiktdan farqli: u
 *  API'dan keladi va yangi kod qo'shilishi mumkin). */
export function statusOf(key: string | undefined | null): StatusDef {
  const k = String(key ?? "").toLowerCase() as StatusKey;
  return STATUSES[k] ?? STATUSES.info;
}

export function isStatusKey(value: unknown): value is StatusKey {
  return KEYS.includes(value as StatusKey);
}

/** 10 xil ko'rinish (D60). `auto` — ekranga qarab tanlaydi.
 *
 *  | # | id         | Ko'rinish                    |
 *  |---|------------|------------------------------|
 *  | ① | `text`     | faqat rangli matn            |
 *  | ② | `iconText` | ikonka + rang + matn         |
 *  | ③ | `badge`    | to'ldirilgan yumaloq nishon  |
 *  | ④ | `circle`   | rangli doira + oq ikonka     |
 *  | ⑤ | `dot`      | rangli nuqta + matn          |
 *  | ⑥ | `box`      | ramkali kvadrat + ikonka     |
 *  | ⑦ | `alert`    | chap chiziq + ikonka + matn  |
 *  | ⑧ | `soft`     | yumshoq fonli karta          |
 *  | ⑨ | `outline`  | ramkali karta                |
 *  | ⑩ | `stack`    | katta karta (ustma-ust)      |
 */
export type StatusVariant =
  | "auto"
  | "text"
  | "iconText"
  | "badge"
  | "circle"
  | "dot"
  | "box"
  | "alert"
  | "soft"
  | "outline"
  | "stack";

export const STATUS_VARIANTS: { id: StatusVariant; labelKey: string; hintKey: string }[] = [
  { id: "auto", labelKey: "status.style.auto", hintKey: "status.style.autoHint" },
  { id: "text", labelKey: "status.style.text", hintKey: "status.style.textHint" },
  { id: "iconText", labelKey: "status.style.iconText", hintKey: "status.style.iconTextHint" },
  { id: "badge", labelKey: "status.style.badge", hintKey: "status.style.badgeHint" },
  { id: "circle", labelKey: "status.style.circle", hintKey: "status.style.circleHint" },
  { id: "dot", labelKey: "status.style.dot", hintKey: "status.style.dotHint" },
  { id: "box", labelKey: "status.style.box", hintKey: "status.style.boxHint" },
  { id: "alert", labelKey: "status.style.alert", hintKey: "status.style.alertHint" },
  { id: "soft", labelKey: "status.style.soft", hintKey: "status.style.softHint" },
  { id: "outline", labelKey: "status.style.outline", hintKey: "status.style.outlineHint" },
  { id: "stack", labelKey: "status.style.stack", hintKey: "status.style.stackHint" },
];

export const DEFAULT_STATUS_VARIANT: StatusVariant = "auto";

export function clampStatusVariant(value: unknown): StatusVariant {
  return STATUS_VARIANTS.some((v) => v.id === value)
    ? (value as StatusVariant)
    : DEFAULT_STATUS_VARIANT;
}
