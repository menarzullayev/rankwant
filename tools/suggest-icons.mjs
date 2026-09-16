// For each (pack, key) that failed to resolve, search that pack's real icon
// list for plausible names and print them, so the candidate lists can be
// fixed in bulk instead of one key at a time.
//
// The search terms come from the key itself plus the names the key already
// resolved to in the OTHER packs — if Tabler calls it `circle-x`, then
// `circle`, `x` and `circle-x` are all worth probing in Heroicons.
import fs from "node:fs";
import { KEYS } from "./icon-keys.mjs";

import { MISSES, PACK_LISTS as CACHE, RESOLVED } from "./icon-paths.mjs";

const lists = {};
const leafOf = (n) => n.slice(n.lastIndexOf("/") + 1);
for (const f of fs.readdirSync(CACHE)) {
  const pack = f.replace(".json", "");
  lists[pack] = JSON.parse(fs.readFileSync(`${CACHE}/${f}`, "utf8")).map((x) => x.leaf);
}

const resolved = JSON.parse(
  fs.readFileSync(RESOLVED, "utf8")
);

// Build a probe vocabulary per key: the key's own words + every name the key
// resolved to elsewhere + the first candidates.
const probes = {};
for (const [key, def] of Object.entries(KEYS)) {
  const words = new Set();
  const obj = key.split(".")[1] || "";
  // camelCase -> words
  for (const w of obj.split(/(?=[A-Z])/)) if (w.length > 2) words.add(w.toLowerCase());
  for (const c of def.c) for (const w of c.split("-")) if (w.length > 2) words.add(w);
  for (const p of Object.keys(resolved)) {
    const got = resolved[p][key];
    if (got) for (const w of leafOf(got).split("-")) if (w.length > 2) words.add(w);
  }
  probes[key] = [...words];
}

const misses = fs
  .readFileSync(MISSES, "utf8")
  .trim()
  .split("\n")
  .map((l) => {
    const m = l.match(/^([a-zA-Z]+): ([a-z.]+) /);
    return m ? { pack: m[1], key: m[2] } : null;
  })
  .filter(Boolean);

// Group by key so the suggestion is written once per key.
const byKey = {};
for (const { pack, key } of misses) (byKey[key] ||= []).push(pack);

let shown = 0;
for (const [key, packs] of Object.entries(byKey)) {
  const words = probes[key];
  console.log(`\n── ${key}  [${packs.join(", ")}]`);
  for (const pack of packs) {
    const hits = lists[pack]
      .filter((n) => words.some((w) => n.includes(w)))
      // Prefer names that start with a probe word — closer to the concept.
      .sort((a, b) => {
        const sa = words.some((w) => a.startsWith(w)) ? 0 : 1;
        const sb = words.some((w) => b.startsWith(w)) ? 0 : 1;
        return sa - sb || a.length - b.length;
      })
      .slice(0, 7);
    console.log(`   ${pack.padEnd(15)} ${hits.join(" · ") || "(mos yo'q)"}`);
  }
  if (++shown >= 45) {
    console.log(`\n… yana ${Object.keys(byKey).length - shown} kalit`);
    break;
  }
}
