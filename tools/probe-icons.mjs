// Probe specific icon names against a pack's real list.
// Usage: node tools/probe-icons.mjs heroicons wifi arrow-trending-up bold
import fs from "node:fs";

import { PACK_LISTS as CACHE } from "./icon-paths.mjs";
const [pack, ...names] = process.argv.slice(2);
if (!pack) {
  console.error("ishlatish: node tools/probe-icons.mjs <pack> <nom> [nom...]");
  process.exit(1);
}
const list = JSON.parse(fs.readFileSync(`${CACHE}/${pack}.json`, "utf8")).map((x) => x.leaf);
const set = new Set(list);
for (const n of names) {
  console.log(`${set.has(n) ? "✓" : "✕"} ${n}`);
}
// If a name is missing, show the closest alternatives.
const missing = names.filter((n) => !set.has(n));
if (missing.length) {
  console.log("\nYaqin nomzodlar:");
  for (const n of missing) {
    const parts = n.split("-").filter((p) => p.length > 2);
    const near = list
      .filter((x) => parts.some((p) => x.includes(p)))
      .sort((a, b) => a.length - b.length)
      .slice(0, 8);
    console.log(`  ${n.padEnd(26)} ${near.join(" · ")}`);
  }
}
