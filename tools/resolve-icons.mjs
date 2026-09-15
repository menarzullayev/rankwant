// Resolve every semantic key to a concrete icon name in every pack.
//
// This is the step that decides whether the pack system is real or
// aspirational: an icon with no match in a pack cannot be swapped, and D12
// says there is no silent fallback. So the script reports misses loudly
// rather than picking something close.
//
// ⚠️ `brand.*` keys are skipped here. They are logos (Python, GitHub …),
// which no interface pack contains — Phosphor has no Python glyph. They are
// generated separately from Simple Icons.
import fs from "node:fs";
import { KEYS, PACK_SOURCES, CATEGORIES } from "./icon-keys.mjs";
import { PACK_OVERRIDES } from "./icon-overrides.mjs";

const CACHE = "C:/Users/nsn/project/cp/.tmp-verdict/pack-lists";

async function fetchJson(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status} ${url}`);
  return r.json();
}

async function names(pack) {
  const file = `${CACHE}/${pack}.json`;
  if (fs.existsSync(file)) return JSON.parse(fs.readFileSync(file, "utf8"));
  const src = PACK_SOURCES[pack];
  const data = await fetchJson(src.list);
  const paths = data.files
    .map((f) => f.name)
    .filter((n) => n.startsWith(src.prefix) && n.endsWith(".svg"))
    .map((n) => n.slice(src.prefix.length, -4));
  // Match on the leaf name (`System/search` -> `search`) but REMEMBER the
  // full path, because Remix's URL needs the category folder.
  const out = paths.map((n) => {
    const leaf = n.slice(n.lastIndexOf("/") + 1);
    return { leaf: leaf.replace(/-fill$|-line$|-outline$|-duotone$/, ""), path: n };
  });
  fs.writeFileSync(file, JSON.stringify(out, null, 0));
  return out;
}

/** Pick the first candidate the pack actually has, and return the path
 *  the CDN needs (Remix groups icons into category folders). */
function resolve(candidates, available) {
  const byLeaf = new Map(available.map((a) => [a.leaf, a.path]));
  for (const c of candidates) if (byLeaf.has(c)) return byLeaf.get(c);
  return null;
}

// Brand keys belong to Simple Icons, not to the interface packs.
const interfaceKeys = Object.entries(KEYS).filter(([k]) => !k.startsWith("brand."));
const brandKeys = Object.entries(KEYS).filter(([k]) => k.startsWith("brand."));

const packs = Object.keys(PACK_SOURCES);
const result = {};
const misses = [];

for (const pack of packs) {
  const avail = await names(pack);
  result[pack] = {};
  let hit = 0;
  const overrides = PACK_OVERRIDES[pack] ?? {};
  for (const [key, def] of interfaceKeys) {
    // Measured names win over the generic guesses: the override was checked
    // against this pack's real file list, the candidate list was not.
    const got = resolve([...(overrides[key] ?? []), ...def.c], avail);
    result[pack][key] = got;
    if (got) hit++;
    else misses.push(`${pack}: ${key} (${def.c.slice(0, 3).join(", ")})`);
  }
  const pct = Math.round((hit / interfaceKeys.length) * 100);
  console.log(
    `${pack.padEnd(16)} ${String(hit).padStart(3)}/${interfaceKeys.length}  ${String(pct).padStart(3)}%  (mavjud: ${avail.length})`
  );
}

fs.writeFileSync(
  "C:/Users/nsn/project/cp/.tmp-verdict/pack-resolved.json",
  JSON.stringify(result, null, 2) + "\n"
);

// Per-category breakdown — shows where the gaps cluster.
console.log("\nKategoriya bo'yicha:");
for (const cat of CATEGORIES) {
  const keys = interfaceKeys.filter(([k]) => k.split(".")[0] === cat.id);
  if (!keys.length) {
    if (cat.id === "brand") {
      console.log(`  ${cat.name.padEnd(26)} ${brandKeys.length} kalit — Simple Icons`);
    }
    continue;
  }
  const full = packs.filter((p) => keys.every(([k]) => result[p][k])).length;
  console.log(
    `  ${cat.name.padEnd(26)} ${String(keys.length).padStart(3)} kalit · ${full}/${packs.length} to'plamda to'liq`
  );
}

console.log(`\nInterfeys kalitlari: ${interfaceKeys.length} × ${packs.length} to'plam`);
console.log(`Brend kalitlari:    ${brandKeys.length} (Simple Icons)`);
console.log(`Yetishmagan:        ${misses.length}`);
if (misses.length) {
  const byPack = {};
  for (const m of misses) {
    const p = m.split(":")[0];
    byPack[p] = (byPack[p] || 0) + 1;
  }
  console.log("  To'plam bo'yicha:", JSON.stringify(byPack));
  fs.writeFileSync(
    "C:/Users/nsn/project/cp/.tmp-verdict/pack-misses.txt",
    misses.join("\n") + "\n"
  );
}
