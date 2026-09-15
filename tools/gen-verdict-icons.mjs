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
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(here, "phosphor-verdict-icons.json");
const OUT = path.join(here, "..", "apps", "web", "src", "icons", "verdict-icons.tsx");

const icons = JSON.parse(fs.readFileSync(SRC, "utf8"));

// Phosphor name -> exported component name.
const NAME = {
  "check-circle": "VerdictAcceptedIcon",
  "x-circle": "VerdictWrongIcon",
  timer: "VerdictTimeIcon",
  cpu: "VerdictMemoryIcon",
  "warning-octagon": "VerdictRuntimeIcon",
  wrench: "VerdictCompileIcon",
  ruler: "VerdictFormatIcon",
  "upload-simple": "VerdictOutputIcon",
  gear: "VerdictInternalIcon",
  hourglass: "VerdictPendingIcon",
};

// Verdict key -> component name (order defines the mapping block).
const KEY = {
  AC: "VerdictAcceptedIcon",
  WA: "VerdictWrongIcon",
  TLE: "VerdictTimeIcon",
  MLE: "VerdictMemoryIcon",
  RE: "VerdictRuntimeIcon",
  CE: "VerdictCompileIcon",
  PE: "VerdictFormatIcon",
  OLE: "VerdictOutputIcon",
  IE: "VerdictInternalIcon",
  PD: "VerdictPendingIcon",
};

// Raw SVG attributes -> JSX camelCase.
const toJsx = (body) =>
  body
    .replace(/fill-rule=/g, "fillRule=")
    .replace(/clip-rule=/g, "clipRule=")
    .replace(/stroke-width=/g, "strokeWidth=")
    .replace(/stroke-linecap=/g, "strokeLinecap=")
    .replace(/stroke-linejoin=/g, "strokeLinejoin=");

const missing = Object.keys(NAME).filter((k) => !icons[k]);
if (missing.length) {
  console.error("Yetishmayotgan ikonkalar:", missing.join(", "));
  process.exit(1);
}

const parts = Object.entries(NAME)
  .map(([k, name]) => {
    return `
/** Phosphor \`${k}\` (MIT). Verdikt ikonkasi — ${name}. */
export const ${name} = (p: IconProps) => (
  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">
    ${toJsx(icons[k])}
  </svg>
);`;
  })
  .join("\n");

const mapping = Object.entries(KEY)
  .map(([key, name]) => `  ${key}: ${name},`)
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
 */

type IconProps = { className?: string };

const base = {
  viewBox: "0 0 256 256",
  fill: "currentColor",
  xmlns: "http://www.w3.org/2000/svg",
};
${parts}

/** Verdikt kaliti → ikonka komponenti. */
export const VERDICT_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {
${mapping}
};
`;

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, file);
console.log("yozildi:", path.relative(path.join(here, ".."), OUT).replace(/\\/g, "/"));
console.log("ikonkalar:", Object.keys(NAME).length);
