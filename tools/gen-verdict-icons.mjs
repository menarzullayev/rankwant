// Regenerate `apps/web/src/icons/phosphor.tsx` from a curated Phosphor
// (MIT) subset. The subset lives beside this script so the build is
// reproducible without network access.
//
//   node tools/gen-verdict-icons.mjs
//
// Phosphor is drawn on a 256x256 grid with `fill="currentColor"`; other
// viewBoxes distort the stroke weight, so we keep it as-is.
//
// NOTE: the data file is NOT under `tools/data/` on purpose — `.gitignore`
// has a bare `data/` rule (meant for local DB/media), which would silently
// swallow it and break the build on a fresh clone.
//
// ⚠️ `CODE_ICON` must stay in step with `apps/api/judging/verdicts.py`.
// A code missing here falls back to a question mark and the user sees the
// wrong verdict — `tools/check_verdict_codes.py` guards that.
//
// One module, two domains: judge verdicts and UI status share the same
// glyphs (`check-circle`, `x-circle`), so emitting them twice would mean
// two copies of the same path drifting apart.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(here, "phosphor-verdict-icons.json");
const OUT = path.join(here, "..", "apps", "web", "src", "icons", "phosphor.tsx");

const icons = JSON.parse(fs.readFileSync(SRC, "utf8"));

// Verdict code -> Phosphor icon name. Several codes share one icon on
// purpose: `RE`, `RE_SIGNAL` and `RE_EXIT` are all runtime failures, and
// the label (not the glyph) is what distinguishes them.
const CODE_ICON = {
  PENDING: "hourglass",
  RUNNING: "spinner-gap",
  AC: "check-circle",
  WA: "x-circle",
  TLE: "timer",
  MLE: "cpu",
  OLE: "upload-simple",
  RE: "warning-octagon",
  RE_SIGNAL: "warning-octagon",
  RE_EXIT: "warning-octagon",
  CE: "wrench",
  PE: "ruler",
  PARTIAL: "chart-pie",
  IE: "gear",
  WRONG_TEST: "test-tube",
  SKIPPED: "skip-forward",
  COMPILE_TIMEOUT: "clock-countdown",
  IDLENESS: "moon",
  SECURITY_VIOLATION: "shield-warning",
  CHECKER_ERROR: "bug",
  TESTING_ABORTED: "prohibit",
  RATE_LIMITED: "gauge",
  DENIAL_OF_JUDGEMENT: "cloud-slash",
};

// UI status -> Phosphor icon name. Deliberately a different palette of
// glyphs from the verdicts: `status.warn` is a triangle, `TLE` is a timer.
const STATUS_ICON = {
  ok: "check-circle",
  warn: "warning",
  bad: "x-circle",
  info: "info",
};

const camel = (s) =>
  s
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join("");

// Icons that are not tied to a code but are still needed by the components.
// `question` is the explicit "we do not know this code" glyph — an unknown
// verdict must never silently borrow a real verdict's icon.
const EXTRA_ICONS = [
  "question",
  "folder-open",
  "warning-circle",
  "magnifying-glass",
  "tray",
  "users",
  "note",
  "archive",
  "bell-slash",
  "funnel",
  "caret-down",
  "x",
  "plus",
  "download-simple",
  "squares-four",
  "list",
  "table",
  "arrows-down-up",
];

// Empty-state illustration -> Phosphor icon name. Callers pass a key, so a
// page cannot invent a glyph that the generator never emitted.
const EMPTY_ICON = {
  empty: "folder-open",
  error: "warning-circle",
  search: "magnifying-glass",
  list: "tray",
  people: "users",
  note: "note",
  archive: "archive",
  silent: "bell-slash",
};

// Search / filter / table affordances (D61). Kept in one map so the eight
// patterns share one glyph per meaning.
const UI_ICON = {
  search: "magnifying-glass",
  filter: "funnel",
  sort: "arrows-down-up",
  sortDesc: "caret-down",
  clear: "x",
  add: "plus",
  download: "download-simple",
  viewGrid: "squares-four",
  viewList: "list",
  viewTable: "table",
};

const distinct = [
  ...new Set([
    ...Object.values(CODE_ICON),
    ...Object.values(STATUS_ICON),
    ...Object.values(EMPTY_ICON),
    ...Object.values(UI_ICON),
    ...EXTRA_ICONS,
  ]),
].sort();
const compName = (ph) => `Ph${camel(ph)}`;

const missing = distinct.filter((k) => !icons[k]);
if (missing.length) {
  console.error("Yetishmayotgan ikonkalar:", missing.join(", "));
  process.exit(1);
}

// Raw SVG attributes -> JSX camelCase.
const toJsx = (body) =>
  body
    .replace(/fill-rule=/g, "fillRule=")
    .replace(/clip-rule=/g, "clipRule=")
    .replace(/stroke-width=/g, "strokeWidth=")
    .replace(/stroke-linecap=/g, "strokeLinecap=")
    .replace(/stroke-linejoin=/g, "strokeLinejoin=");

const parts = distinct
  .map(
    (k) => `
/** Phosphor \`${k}\` (MIT). */
export const ${compName(k)} = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    ${toJsx(icons[k])}
  </svg>
);`
  )
  .join("\n");

const map = (obj) =>
  Object.entries(obj)
    .map(([k, ph]) => `  ${k}: ${compName(ph)},`)
    .join("\n");

const file = `/** Phosphor ikonkalari (MIT), 256×256 to'r, \`fill="currentColor"\`.
 *
 *  Generatsiya qilingan — \`tools/gen-verdict-icons.mjs\` bilan qayta yasash
 *  mumkin. Qo'lda tahrirlanmaydi.
 *
 *  Nega 256×256: Phosphor shu to'rda chizilgan — boshqa o'lchamga
 *  masshtablashda chiziq qalinligi buziladi.
 *
 *  Nega bitta fayl, ikki xarita: judge verdikti ham, interfeys holati ham
 *  bir xil glifdan foydalanadi (\`check-circle\`, \`x-circle\`). Ikkita fayl
 *  qilinsa o'sha yo'l ikki nusxada yashab, vaqt o'tib ajralib ketardi.
 *
 *  ${distinct.length} ta ikonka · ${Object.keys(CODE_ICON).length} verdikt kodi ·
 *  ${Object.keys(STATUS_ICON).length} holat.
 */

type IconProps = { className?: string };

const base = {
  viewBox: "0 0 256 256",
  fill: "currentColor",
  xmlns: "http://www.w3.org/2000/svg",
};
${parts}

/** Verdikt kaliti → ikonka. Kalitlar \`apps/api/judging/verdicts.py\` bilan
 *  bir xil bo'lishi shart (\`tools/check_verdict_codes.py\`). */
export const VERDICT_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
${map(CODE_ICON)}
};

/** Interfeys holati → ikonka (\`lib/theme/status.ts\`). */
export const STATUS_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
${map(STATUS_ICON)}
};

/** Bo'sh holat rasmchasi → ikonka (\`components/ui/EmptyState.tsx\`). */
export const EMPTY_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
${map(EMPTY_ICON)}
};

/** Qidiruv / filtr / jadval ikonkalari (\`components/ui/\`). */
export const UI_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
${map(UI_ICON)}
};
`;

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, file);
console.log("yozildi:", path.relative(path.join(here, ".."), OUT).replace(/\\/g, "/"));
console.log(
  "kodlar:",
  Object.keys(CODE_ICON).length,
  "| holatlar:",
  Object.keys(STATUS_ICON).length,
  "| ikonkalar:",
  distinct.length
);
