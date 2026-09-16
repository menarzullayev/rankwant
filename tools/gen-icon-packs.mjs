// Generate one module per icon pack, from the CDN, at build-authoring time.
//
// Why generate instead of installing the packages: ten icon libraries is
// roughly 20 MB of node_modules and tens of thousands of files, of which we
// use 44 per pack. Generating a subset keeps the repo small, adds no
// runtime dependency, and follows the pattern already proven by
// `phosphor.tsx` + `gen-verdict-icons.mjs`.
//
// D17 (dynamic loading) still holds: each generated file is its own module,
// so only the selected pack is pulled into the client bundle.
import fs from "node:fs";
import path from "node:path";

import { RESOLVED, SVG_CACHE as CACHE, WEB_SRC } from "./icon-paths.mjs";

const OUT = path.join(WEB_SRC, "icons", "packs");

/** Pack -> prefix, base svg props, and the CDN url builder. */
const PACKS = {
  lucide: {
    prefix: "Lu",
    label: "Lucide",
    license: "ISC",
    base: { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2 },
    url: (n) => `https://cdn.jsdelivr.net/npm/lucide-static@0.544.0/icons/${n}.svg`,
  },
  tabler: {
    prefix: "Tb",
    label: "Tabler",
    license: "MIT",
    base: { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2 },
    url: (n) => `https://cdn.jsdelivr.net/npm/@tabler/icons@3.34.1/icons/outline/${n}.svg`,
  },
  heroicons: {
    prefix: "Hi",
    label: "Heroicons (outline)",
    license: "MIT",
    base: { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.5 },
    url: (n) => `https://cdn.jsdelivr.net/npm/heroicons@2.2.0/24/outline/${n}.svg`,
  },
  heroiconsSolid: {
    prefix: "HiS",
    label: "Heroicons (solid)",
    license: "MIT",
    base: { viewBox: "0 0 24 24", fill: "currentColor" },
    url: (n) => `https://cdn.jsdelivr.net/npm/heroicons@2.2.0/24/solid/${n}.svg`,
  },
  bootstrap: {
    prefix: "Bi",
    label: "Bootstrap Icons",
    license: "MIT",
    base: { viewBox: "0 0 16 16", fill: "currentColor" },
    url: (n) => `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/icons/${n}.svg`,
  },
  remix: {
    prefix: "Ri",
    label: "Remix Icon",
    license: "Apache-2.0",
    base: { viewBox: "0 0 24 24", fill: "currentColor" },
    url: (n) => `https://cdn.jsdelivr.net/npm/remixicon@4.6.0/icons/${n}.svg`,
  },
  // Phosphorning uch uslubi — uchta ALOHIDA fayl to'plami. Ilgari uchtasi
  // bitta xaritaga ulangan edi va tanlov hech narsani o'zgartirmasdi.
  phosphor: {
    prefix: "Ph",
    label: "Phosphor",
    license: "MIT",
    base: { viewBox: "0 0 256 256", fill: "currentColor" },
    url: (n) => `https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1/assets/regular/${n}.svg`,
  },
  phosphorSolid: {
    prefix: "PhF",
    label: "Phosphor Solid",
    license: "MIT",
    base: { viewBox: "0 0 256 256", fill: "currentColor" },
    url: (n) => `https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1/assets/fill/${n}.svg`,
  },
  phosphorDuotone: {
    prefix: "PhD",
    label: "Phosphor Duotone",
    license: "MIT",
    base: { viewBox: "0 0 256 256", fill: "currentColor" },
    url: (n) => `https://cdn.jsdelivr.net/npm/@phosphor-icons/core@2.1.1/assets/duotone/${n}.svg`,
  },
};

/** `Arrows/arrow-left` -> `ArrowLeft`; the category is a URL detail. */
const leafOf = (n) => n.slice(n.lastIndexOf("/") + 1);
const pascal = (s) =>
  leafOf(s)
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join("");

/** SVG attribute names that need camelCase for JSX. */
const ATTR = {
  "stroke-width": "strokeWidth",
  "stroke-linecap": "strokeLinecap",
  "stroke-linejoin": "strokeLinejoin",
  "stroke-miterlimit": "strokeMiterlimit",
  "fill-rule": "fillRule",
  "clip-rule": "clipRule",
  "fill-opacity": "fillOpacity",
  "stroke-opacity": "strokeOpacity",
  "clip-path": "clipPath",
};

function toJsx(inner) {
  let s = inner;
  // Drop attributes the wrapper already sets, and non-JSX ones.
  s = s.replace(/\s(?:class|width|height|xmlns)="[^"]*"/g, "");
  s = s.replace(/\sfill="currentColor"/g, "");
  s = s.replace(/\sstroke="currentColor"/g, "");
  s = s.replace(/\saria-hidden="[^"]*"/g, "");
  s = s.replace(/\sdata-slot="[^"]*"/g, "");
  s = s.replace(/\sfill="none"/g, "");
  for (const [k, v] of Object.entries(ATTR)) s = new RegExp(`\\s${k}=`, "g") && (s = s.split(` ${k}=`).join(` ${v}=`));
  // `style="..."` with multiple declarations cannot be passed as a string.
  s = s.replace(/\sstyle="([^"]*)"/g, (_m, css) => {
    const props = css
      .split(";")
      .filter(Boolean)
      .map((d) => {
        const [k, v] = d.split(":");
        const key = k.trim().replace(/-([a-z])/g, (_x, c) => c.toUpperCase());
        return `${key}: ${JSON.stringify(v.trim())}`;
      })
      .join(", ");
    return ` style={{ ${props} }}`;
  });
  return s
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .join("\n    ");
}

async function svgFor(pack, name) {
  const dir = `${CACHE}/${pack}`;
  fs.mkdirSync(dir, { recursive: true });
  // Remix names carry a folder (`Arrows/arrow-left`); flatten it for the
  // cache filename so we do not create a directory tree for it.
  const file = `${dir}/${name.replace(/\//g, "__")}.svg`;
  if (fs.existsSync(file)) return fs.readFileSync(file, "utf8");
  const r = await fetch(PACKS[pack].url(name));
  if (!r.ok) throw new Error(`${pack}/${name}: ${r.status}`);
  const text = await r.text();
  fs.writeFileSync(file, text);
  return text;
}

function parseSvg(svg) {
  const open = svg.match(/<svg\b[^>]*>/);
  const viewBox = open?.[0].match(/viewBox="([^"]+)"/)?.[1];
  const start = svg.indexOf(open[0]) + open[0].length;
  const end = svg.lastIndexOf("</svg>");
  return { viewBox, inner: svg.slice(start, end) };
}

const resolved = JSON.parse(fs.readFileSync(RESOLVED, "utf8"));
fs.mkdirSync(OUT, { recursive: true });

let total = 0;
for (const [pack, cfg] of Object.entries(PACKS)) {
  const map = resolved[pack];
  const keys = Object.keys(map).sort();
  const lines = [];
  const seen = new Map();

  for (const key of keys) {
    const name = map[key];
    if (!name) continue;
    const svg = await svgFor(pack, name);
    const { viewBox, inner } = parseSvg(svg);
    if (viewBox && viewBox !== cfg.base.viewBox) {
      console.log(`  ⚠️  ${pack}/${name}: viewBox ${viewBox} (base ${cfg.base.viewBox})`);
    }
    const comp = cfg.prefix + pascal(name);
    if (!seen.has(name)) {
      seen.set(name, comp);
      lines.push(
        `/** ${cfg.label} \`${name}\` (${cfg.license}). */\n` +
          `export const ${comp} = (p: IconProps) => (\n` +
          `  <svg {...base} className={p.className ?? "size-5"} aria-hidden="true">\n` +
          `    ${toJsx(inner)}\n` +
          `  </svg>\n` +
          `);\n`
      );
    }
  }

  const mapLines = keys
    .filter((k) => map[k])
    .map((k) => `  "${k}": ${cfg.prefix}${pascal(map[k])},`)
    .join("\n");

  const baseProps = Object.entries(cfg.base)
    .map(([k, v]) => (typeof v === "string" ? `${k}: ${JSON.stringify(v)},` : `${k}: ${v},`))
    .join(" ");
  const strokeExtras =
    cfg.base.stroke !== undefined
      ? ' strokeLinecap: "round" as const, strokeLinejoin: "round" as const,'
      : "";

  const head =
    `/** ${cfg.label} ikonkalari (${cfg.license}), ${cfg.base.viewBox.split(" ").slice(2).join("×")} to'r.\n` +
    ` *\n` +
    ` *  Generatsiya qilingan — \`tools/gen-icon-packs.mjs\` bilan qayta yasash mumkin.\n` +
    ` *  Qo'lda tahrirlanmaydi.\n` +
    ` *\n` +
    ` *  ⚠️ Manba CDN'dan **bir marta** olinadi va shu faylga yoziladi: ilova\n` +
    ` *  ishga tushganda tarmoqqa chiqmaydi, ya'ni yangi dependency ham,\n` +
    ` *  kutubxona yangilanishini kuzatish ham kerak emas.\n` +
    ` *\n` +
    ` *  ${seen.size} ta ikonka.\n` +
    ` */\n\n` +
    `type IconProps = { className?: string };\n\n` +
    `const base = { ${baseProps}${strokeExtras} xmlns: "http://www.w3.org/2000/svg" };\n\n`;

  const tail =
    `\n/** Semantik kalit → ${cfg.label} ikonkasi (D18: \`domen.ob'ekt.holat\`). */\n` +
    `export const ${pack.toUpperCase()}_ICONS: Record<string, (p: IconProps) => React.JSX.Element> = {\n` +
    `${mapLines}\n};\n`;

  // ⚠️ `phosphor` -> `phosphorRegular.tsx`: `icons/phosphor.tsx` allaqachon
  // bor (verdikt + holat to'plami, qo'lda yuritiladi). Bir xil nomda bo'lsa
  // import jimgina noto'g'ri faylni tortardi.
  const stem = pack === "phosphor" ? "phosphorRegular" : pack;
  const file = path.join(OUT, `${stem}.tsx`);
  fs.writeFileSync(file, head + lines.join("\n") + tail);
  total += seen.size;
  console.log(`${pack.padEnd(16)} ${seen.size} ikonka -> icons/packs/${stem}.tsx`);
}
console.log(`\nJami: ${total} komponent`);
