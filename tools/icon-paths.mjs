// Where the icon pipeline reads and writes, relative to this repository.
//
// Until 2026-09-17 every icon tool hard-coded absolute paths into one machine's
// WorkBuddy scratch folder (.tmp-verdict), so the generated packs that say
// "can be regenerated with tools/gen-icon-packs.mjs" could only be regenerated
// there. The cache now defaults to the git-ignored `.tmp/icon-cache`; point
// RANKWANT_ICON_CACHE at an existing cache (for example the old .tmp-verdict
// folder) to reuse downloaded lists and SVGs.
import path from "node:path";
import { fileURLToPath } from "node:url";

export const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const CACHE_DIR =
  process.env.RANKWANT_ICON_CACHE || path.join(REPO, ".tmp", "icon-cache");
export const PACK_LISTS = path.join(CACHE_DIR, "pack-lists");
export const SVG_CACHE = path.join(CACHE_DIR, "svg-cache");
export const RESOLVED = path.join(CACHE_DIR, "pack-resolved.json");
export const MISSES = path.join(CACHE_DIR, "pack-misses.txt");
export const WEB_SRC = path.join(REPO, "apps", "web", "src");
