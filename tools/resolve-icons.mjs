// Resolve every semantic key to a concrete icon name in every pack.
//
// This is the step that decides whether the pack system is real or
// aspirational: an icon that has no match in a pack cannot be swapped, and
// D12 says there is no silent fallback. So the script reports misses
// loudly rather than picking something close.
import fs from "node:fs";
import { KEYS, PACK_SOURCES } from "./icon-keys.mjs";

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

const packs = Object.keys(PACK_SOURCES);
const result = {};
const misses = [];

for (const pack of packs) {
  const avail = await names(pack);
  result[pack] = {};
  let hit = 0;
  for (const [key, cands] of Object.entries(KEYS)) {
    const got = resolve(cands, avail);
    result[pack][key] = got;
    if (got) hit++;
    else misses.push(`${pack}: ${key} (${cands.join(", ")})`);
  }
  console.log(`${pack.padEnd(16)} ${hit}/${Object.keys(KEYS).length}  (mavjud: ${avail.length})`);
}

fs.writeFileSync(
  "C:/Users/nsn/project/cp/.tmp-verdict/pack-resolved.json",
  JSON.stringify(result, null, 2) + "\n"
);

console.log(`\nJami kalit: ${Object.keys(KEYS).length} × ${packs.length} to'plam`);
console.log(`Topilmadi: ${misses.length}`);
for (const m of misses.slice(0, 30)) console.log("  ✕ " + m);
