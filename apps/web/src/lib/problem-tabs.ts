/** Masala bo'limlari — manzil ↔ tab (SOF modul).
 *
 *  `lib/auth-tabs.ts` bilan bir xil naqsh: bu faylda na `"use client"`,
 *  na React importi bor — faqat ro'yxat va tekshiruv. `ProblemTabs`
 *  (server komponent) va sahifalar bo'lim nomlarini shu yerdan oladi.
 *  Ikki joyda yozilsa, biri o'zgarganda ikkinchisi jimgina eskirib qolardi.
 *
 *  Kanonik manzil — `/problems/[slug]?tab=<id>`:
 *  - `?tab=` bo'lmasa `description` ochiladi, ya'ni `/problems/slug`
 *    ni yoddan yozgan odam ham to'g'ri joyga tushadi;
 *  - noma'lum qiymat ham `description` ga tushadi (bo'sh panel emas);
 *  - tab almashish `<Link scroll={false}>` — to'liq qayta yuklash yo'q,
 *    Back/Forward va yangilash tab holatini saqlaydi.
 *
 *  Eski yo'llar (`/status`, `/stats`, `/solvers` sahifalari va
 *  `statement`/`status`/`stats` nomlari) shu yerga normalizatsiya
 *  qilinadi — ulashilgan havolalar 404 emas, kanonik tabga tushadi.
 */

export const PROBLEM_TABS = [
  "description",
  "attempts",
  "editorial",
  "statistics",
  "solvers",
] as const;
export type ProblemTab = (typeof PROBLEM_TABS)[number];

/** `?tab=` bo'lmasa yoki noto'g'ri bo'lsa shu. */
export const DEFAULT_PROBLEM_TAB: ProblemTab = "description";

/** Eski nom → kanonik. `solvers` ikkalasida ham bir xil. */
const LEGACY_ALIAS: Record<string, ProblemTab> = {
  statement: "description",
  status: "attempts",
  stats: "statistics",
  solvers: "solvers",
};

/** Manzil qatoridagi `?tab=` ni bo'limga aylantiradi — SOF funksiya.
 *
 *  Noma'lum/bo'sh qiymat `null` qaytaradi, ya'ni chaqiruvchi standart
 *  holatga tushadi. Buzuq qiymatni jimgina qabul qilish bo'sh panel
 *  ko'rsatardi: bo'lim faqat ro'yxatdagi beshtadan biri bo'lishi mumkin.
 */
export function parseProblemTab(
  raw: string | string[] | null | undefined,
): ProblemTab | null {
  const value = Array.isArray(raw) ? raw[0] : raw;
  if (!value) return null;
  if ((PROBLEM_TABS as readonly string[]).includes(value)) {
    return value as ProblemTab;
  }
  const aliased = LEGACY_ALIAS[value];
  return aliased ?? null;
}

/** Sahifa o'qiydigan shakl: noma'lum/bo'sh → `description`. */
export function resolveProblemTab(
  raw: string | string[] | null | undefined,
): ProblemTab {
  return parseProblemTab(raw) ?? DEFAULT_PROBLEM_TAB;
}

/** Tab havolasi. `description` — yalang'och manzil (SEO kanonik toza
 *  qoladi), qolganlari `?tab=` bilan. `contest` — musobaqadan kelgan
 *  kontekst — saqlanadi; tabga xos filtrlar (verdict, ordering, …)
 *  ataylab tashlanadi: ular boshqa tabda ma'nosiz va URL ni ifloslantiradi.
 */
export function buildProblemTabHref(
  slug: string,
  tab: ProblemTab,
  extra?: { contest?: string | null },
): string {
  const params = new URLSearchParams();
  if (tab !== DEFAULT_PROBLEM_TAB) params.set("tab", tab);
  if (extra?.contest) params.set("contest", extra.contest);
  const query = params.toString();
  return `/problems/${slug}${query ? `?${query}` : ""}`;
}

/** Urinishlar ro'yxati havolasi (`tab=attempts` har doim ichida).
 *
 *  `AttemptFilters`/`AttemptTable` shu yerdan quradi — qo'lda
 *  `/status` yozilsa, eski sahifaga tushib, tab holati yo'qolardi.
 *  `cursor` har doim tashlanadi: eski kursor yangi ro'yxatning boshqa
 *  joyiga ishora qilardi.
 */
export function buildAttemptsHref(
  slug: string,
  filters: Record<string, string | undefined>,
): string {
  const params = new URLSearchParams();
  params.set("tab", "attempts");
  for (const [key, value] of Object.entries(filters)) {
    if (key === "cursor") continue;
    if (value) params.set(key, value);
  }
  return `/problems/${slug}?${params}`;
}

/** The attempts list an attempt table lives on: a problem's tab when
 *  `slug` is given, the site-wide feed (`/attempts`) otherwise. One
 *  builder for both, so the table and its filters cannot disagree about
 *  where they are. `cursor` is dropped for the same reason as above.
 */
export function buildAttemptListHref(
  slug: string | undefined,
  filters: Record<string, string | undefined>,
): string {
  if (slug) return buildAttemptsHref(slug, filters);
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (key === "cursor") continue;
    if (value) params.set(key, value);
  }
  const query = params.toString();
  return query ? `/attempts?${query}` : "/attempts";
}

/** Yechganlar saralash havolasi (`tab=solvers` har doim ichida). */
export function buildSolversHref(slug: string, ordering: string): string {
  return `/problems/${slug}?tab=solvers&ordering=${encodeURIComponent(ordering)}`;
}
