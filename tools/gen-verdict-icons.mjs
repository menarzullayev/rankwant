// Regenerate `apps/web/src/icons/verdict-icons.tsx` from a curated
// Phosphor (MIT) subset. The subset lives beside this script so the build
// is reproducible without network access.
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
// ⚠️ The code list must stay in step with `apps/api/judging/verdicts.py`.
// A code missing here falls back to PENDING and the user sees the wrong
// verdict — `tools/check_verdict_codes.py` guards that.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(here, "phosphor-verdict-icons.json");
const OUT = path.join(here, "..", "apps", "web", "src", "icons", "verdict-icons.tsx");

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

const camel = (s) =>
  s
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join("");

// Icons that are not tied to a code but are still needed by the component.
// `question` is the explicit "we do not know this code" glyph — an unknown
// verdict must never silently borrow a real verdict's icon.
const EXTRA_ICONS = ["question"];

// One component per distinct icon, named after the icon.
const distinct = [...new Set([...Object.values(CODE_ICON), ...EXTRA_ICONS])].sort();
const compName = (ph) => `VerdictIcon${camel(ph)}`;

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

const mapping = Object.entries(CODE_ICON)
  .map(([code, ph]) => `  ${code}: ${compName(ph)},`)
  .join("\n");

const file = `/** Judge verdiktlari ikonkalari.
 *
 *  Manba: **Phosphor** (MIT), 256×256 to'r, \`fill="currentColor"\`.
 *  Generatsiya qilingan — \`tools/gen-verdict-icons.mjs\` bilan qayta yasash mumkin.
 *
 *  ⚠️ Nega alohida fayl: bu ikonkalar **verdikt kalitiga** bog'langan
 *  (\`lib/theme/verdict.ts\`), ya'ni ular birgalikda o'zgaradi. Umumiy
 *  \`icons/index.tsx\` ga aralashtirilsa, aloqa ko'rinmay qolardi.
 *
 *  Nega 256×256: Phosphor shu to'rda chizilgan — boshqa o'lchamga
 *  masshtablashda chiziq qalinligi buziladi.
 *
 *  ${distinct.length} ta ikonka, ${Object.keys(CODE_ICON).length} ta kodga bog'langan.
 */

type IconProps = { className?: string };

const base = {
  viewBox: "0 0 256 256",
  fill: "currentColor",
  xmlns: "http://www.w3.org/2000/svg",
};
${parts}

/** Verdikt kaliti → ikonka komponenti. Kalitlar \`apps/api/judging/verdicts.py\`
 *  bilan bir xil bo'lishi shart. */
export const VERDICT_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
${mapping}
};
`;

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, file);
console.log("yozildi:", path.relative(path.join(here, ".."), OUT).replace(/\\/g, "/"));
console.log("kodlar:", Object.keys(CODE_ICON).length, "| ikonkalar:", distinct.length);
