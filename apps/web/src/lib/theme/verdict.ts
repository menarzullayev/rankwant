/** Judge verdiktlari — yagona ma'lumot manbasi (D56).
 *
 *  Nega alohida fayl: verdikt platformada **bir necha joyda** ko'rinadi —
 *  urinishlar jadvali, masala sahifasi, reyting, natija kartasi. Ilgari har
 *  biri o'z rangini qo'lda yozardi, ya'ni «Accepted» bir joyda yashil,
 *  boshqasida boshqa yashil bo'lishi mumkin edi.
 *
 *  Bu fayl nom, rang va ikonkani bir joyda saqlaydi; ko'rinish esa `Verdict`
 *  komponentida (o'nta variant).
 *
 *  ── Kodlar ro'yxati `apps/api/judging/verdicts.py` bilan AYNAN bir xil
 *  bo'lishi shart. Skript: `python tools/check_verdict_codes.py`.
 *
 *  ⚠️ Notanish kod `PENDING` ga tushadi — lekin **faqat oxirgi chora**
 *  sifatida. Jim yashirish noto'g'ri: `Verdict` komponenti noma'lum kodni
 *  xom holda ko'rsatadi, shunda yangi kod qo'shilganda u «Navbatda» bo'lib
 *  ko'rinmaydi (bir marta shunday bo'lgan: 23 koddan 14 tasi «Pending»
 *  bo'lib ko'ringan edi).
 *
 *  ── Rang guruhi (D56) ataylab **to'rtta**, oltita emas:
 *
 *  | Guruh     | Ma'nosi                                  |
 *  |-----------|------------------------------------------|
 *  | `ok`      | Qabul qilindi                            |
 *  | `warn`    | Hali ketmoqda yoki qisman                |
 *  | `bad`     | **Foydalanuvchi** xatosi                 |
 *  | `neutral` | Infratuzilma / masala nosozligi          |
 *
 *  `neutral` muhim: `IE`, `WRONG_TEST`, `CHECKER_ERROR`, `DENIAL_OF_JUDGEMENT`
 *  odamning aybi EMAS. Ularni qizil ko'rsatish foydalanuvchini bekorga
 *  ayblardi — shuning uchun kulrang.
 *
 *  ⚠️ Ranglar WCAG AA (4.5:1) bo'yicha tanlangan. O'zgartirsang,
 *  `python tools/check_contrast.py` ni ishga tushir.
 */

/** Verdikt kaliti — API shu qiymatlarni qaytaradi. */
export type VerdictKey =
  | "PENDING"
  | "RUNNING"
  | "AC"
  | "WA"
  | "TLE"
  | "MLE"
  | "OLE"
  | "RE"
  | "RE_SIGNAL"
  | "RE_EXIT"
  | "CE"
  | "PE"
  | "HACKED"
  | "PARTIAL"
  | "IE"
  | "WRONG_TEST"
  | "SKIPPED"
  | "COMPILE_TIMEOUT"
  | "IDLENESS"
  | "SECURITY_VIOLATION"
  | "CHECKER_ERROR"
  | "TESTING_ABORTED"
  | "RATE_LIMITED"
  | "DENIAL_OF_JUDGEMENT";

/** To'rt rang guruhi — sabab docstring'da. */
export type VerdictGroup = "ok" | "warn" | "bad" | "neutral";

/** Guruh rangi. `soft` — nishon va karta foni uchun. */
export const VERDICT_GROUPS: Record<VerdictGroup, { color: string; soft: string }> = {
  ok: { color: "#0a6b3d", soft: "#e6f7ee" },
  warn: { color: "#8a5a00", soft: "#fff8e6" },
  bad: { color: "#a32020", soft: "#fdeaea" },
  neutral: { color: "#4b5563", soft: "#f1f3f5" },
};

export type VerdictDef = {
  key: VerdictKey;
  group: VerdictGroup;
  /** To'liq nom — i18n kaliti (`verdict.<KOD>`), 10 tilda mavjud. */
  labelKey: string;
  /** Qisqa izoh — i18n kaliti. Yo'q bo'lsa guruh izohi ishlatiladi. */
  hintKey?: string;
};

/** Guruh izohi — karta ko'rinishida kod izohi bo'lmasa ishlatiladi. */
export const GROUP_HINT_KEY = (g: VerdictGroup) => `verdict.group.${g}.hint`;

const D = (key: VerdictKey, group: VerdictGroup, hintKey?: string): VerdictDef => ({
  key,
  group,
  labelKey: `verdict.${key}`,
  ...(hintKey ? { hintKey } : {}),
});

export const VERDICTS: Record<VerdictKey, VerdictDef> = {
  PENDING: D("PENDING", "neutral"),
  RUNNING: D("RUNNING", "warn"),
  AC: D("AC", "ok", "verdict.hint.AC"),
  WA: D("WA", "bad", "verdict.hint.WA"),
  TLE: D("TLE", "bad", "verdict.hint.TLE"),
  MLE: D("MLE", "bad", "verdict.hint.MLE"),
  OLE: D("OLE", "bad", "verdict.hint.OLE"),
  // `RE` — LEGACY kod, judge endi chiqarmaydi (o'rniga `RE_SIGNAL`/`RE_EXIT`).
  // Bazadagi eski qatorlar uchun qoladi.
  RE: D("RE", "bad", "verdict.hint.RE"),
  RE_SIGNAL: D("RE_SIGNAL", "bad"),
  RE_EXIT: D("RE_EXIT", "bad"),
  CE: D("CE", "bad", "verdict.hint.CE"),
  PE: D("PE", "bad", "verdict.hint.PE"),
  // `bad`, `neutral` emas: test to'g'ri, yiqilgan esa yechim.
  HACKED: D("HACKED", "bad", "verdict.hint.HACKED"),
  PARTIAL: D("PARTIAL", "warn"),
  IE: D("IE", "neutral", "verdict.hint.IE"),
  WRONG_TEST: D("WRONG_TEST", "neutral"),
  SKIPPED: D("SKIPPED", "neutral"),
  COMPILE_TIMEOUT: D("COMPILE_TIMEOUT", "bad"),
  IDLENESS: D("IDLENESS", "bad"),
  SECURITY_VIOLATION: D("SECURITY_VIOLATION", "bad"),
  CHECKER_ERROR: D("CHECKER_ERROR", "neutral"),
  TESTING_ABORTED: D("TESTING_ABORTED", "warn"),
  RATE_LIMITED: D("RATE_LIMITED", "warn"),
  DENIAL_OF_JUDGEMENT: D("DENIAL_OF_JUDGEMENT", "neutral"),
};

/** Kodni normallashtirish: kichik harf, bo'shliq va chiziqcha. */
const normalize = (key: string) => key.trim().toUpperCase().replace(/[\s-]+/g, "_");

/** Verdiktni topadi. Topilmasa — `null`, ya'ni **xom kod ko'rsatiladi**.
 *
 *  Nega `null`, `PENDING` emas: yangi kod qo'shilib, bu fayl yangilanmay
 *  qolsa, u «Navbatda» bo'lib ko'rinardi va buni hech kim sezmasdi.
 *  `null` bo'lsa `Verdict` xom kodni chiqaradi — xato darhol ko'rinadi. */
export function verdictOf(key: string | undefined | null): VerdictDef | null {
  if (key == null) return null;
  const k = normalize(String(key));
  return VERDICTS[k as VerdictKey] ?? null;
}

/** Guruh rangi va foni — `verdictOf` topmagan holat uchun ham ishlaydi. */
export function verdictColors(def: VerdictDef | null): { color: string; soft: string } {
  return VERDICT_GROUPS[def?.group ?? "neutral"];
}

/** Hali natija kutilayotgan kodlar — mijoz shu paytda pollinglaydi.
 *
 *  ⚠️ `TESTING_ABORTED` ham shu yerda: rejudge eski natijani bekor qildi
 *  va yangisi yo'lda. Usiz sahifa eski verdictda qotib qolardi.
 *
 *  Bu `VerdictBadge` dan ko'chirildi (D61): u yerda qolsa, komponent
 *  o'chirilganda polling ham o'chib qolardi. */
const PENDING_CODES = new Set(["PENDING", "RUNNING", "TESTING_ABORTED"]);

export function isPendingVerdict(verdict: string | undefined | null): boolean {
  return PENDING_CODES.has(normalize(String(verdict ?? "")));
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
