// Migrate the app from the hand-drawn icon set to the pack registry (T1).
//
// The hand-drawn set in `icons/index.tsx` is a fixed 1.7-stroke line style.
// The registry serves the same concepts from whichever pack the user picked,
// so after this the Customizer's choice reaches the whole site instead of
// only its own preview.
//
// Two kinds of edit per file:
//   1. `import { CloseIcon } from "@/icons"`  ->  `import { Icon } from "@/components/ui/Icon"`
//   2. `<CloseIcon className="x" />`          ->  `<Icon name="nav.close" className="x" />`
//
// ⚠️ `BrandIcon` is NOT touched. It comes from `lib/tech-icons.tsx` and is a
// brand mark, which D20 ① keeps fixed — it must not follow the pack.
//
// ⚠️ **Why this scans instead of using a regex.** A first attempt matched the
// tag with `<Name\b([^>]*?)/>`, which broke in two ways that only surfaced at
// `tsc`:
//   - a multi-line tag was collapsed onto one line, and
//   - `className={\`… ${open ? "a" : ""}\`}` was cut at the FIRST `}`, which
//     is the one closing `${…}`, not the attribute. The result was a JSX
//     expression left unclosed.
// Both are brace/quote problems, and regexes cannot count. So the tag is
// walked character by character, tracking brace depth and string state.
import fs from "node:fs";
import path from "node:path";

const SRC = "C:/Users/nsn/project/cp/rankwant/apps/web/src";

/** Hand-drawn icon -> semantic key (D18: `domain.object.state`). */
const MAP = {
  ArrowUpIcon: "nav.up",
  BellIcon: "notification.bell",
  BlogIcon: "content.article",
  CheckIcon: "action.confirm",
  ChevronDownIcon: "nav.expandDown",
  CloseIcon: "nav.close",
  ContestIcon: "ranking.trophy",
  CopyIcon: "action.copy",
  FlagIcon: "contest.flag",
  FlameIcon: "ranking.streak",
  GlobeIcon: "locale.globe",
  LeaderboardIcon: "nav.leaderboard",
  LogoutIcon: "user.logout",
  MenuIcon: "nav.menu",
  PaletteIcon: "system.palette",
  ProblemsIcon: "nav.problems",
  QvantIcon: "shop.coin",
  SearchIcon: "action.search",
  SettingsIcon: "system.settings",
  SpinnerIcon: "action.loading",
  StarIcon: "ranking.star",
  UpdatesIcon: "notification.changelog",
  UserIcon: "user.profile",
  WarningIcon: "status.warning",
};

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      if (e.name === "node_modules" || e.name === ".next") continue;
      walk(p, out);
    } else if (e.name.endsWith(".tsx")) out.push(p);
  }
  return out;
}

/** Find the end of the JSX tag that starts at `start` (`<`).
 *  Returns the index just past `/>`, or -1. Tracks braces and quotes so a
 *  `>` inside `{a > b}` or a `}` inside `${…}` cannot end the tag early. */
function findTagEnd(src, start) {
  let depth = 0;
  let quote = null;
  for (let i = start; i < src.length; i++) {
    const c = src[i];
    if (quote) {
      if (c === "\\") i++;
      else if (c === quote) quote = null;
      continue;
    }
    if (c === '"' || c === "'" || c === "`") {
      quote = c;
      continue;
    }
    if (c === "{") depth++;
    else if (c === "}") depth--;
    else if (depth === 0 && c === "/" && src[i + 1] === ">") return i + 2;
  }
  return -1;
}

/** Pull `className=...` out of a tag body, respecting brace nesting. */
function extractClassName(attrs) {
  const at = attrs.indexOf("className=");
  if (at < 0) return null;
  let i = at + "className=".length;
  if (attrs[i] === '"' || attrs[i] === "'") {
    const q = attrs[i];
    const end = attrs.indexOf(q, i + 1);
    return end < 0 ? null : attrs.slice(i, end + 1);
  }
  if (attrs[i] === "{") {
    let depth = 0;
    let quote = null;
    for (let j = i; j < attrs.length; j++) {
      const c = attrs[j];
      if (quote) {
        if (c === "\\") j++;
        else if (c === quote) quote = null;
        continue;
      }
      if (c === '"' || c === "'" || c === "`") quote = c;
      else if (c === "{") depth++;
      else if (c === "}") {
        depth--;
        if (depth === 0) return attrs.slice(i, j + 1);
      }
    }
  }
  return null;
}

const IMPORT_RE = /^import \{([^}]*)\} from "@\/icons";\r?\n/m;

let filesChanged = 0;
const perIcon = {};
const report = [];

for (const file of walk(SRC)) {
  let src = fs.readFileSync(file, "utf8");
  if (!src.includes('from "@/icons"')) continue;

  const m = IMPORT_RE.exec(src);
  if (!m) {
    report.push(`SKIP (import shakli boshqa): ${path.relative(SRC, file)}`);
    continue;
  }

  const names = m[1].split(",").map((s) => s.trim()).filter(Boolean);
  const unknown = names.filter((n) => !MAP[n]);
  if (unknown.length) {
    report.push(`SKIP (xarita yo'q: ${unknown.join(", ")}): ${path.relative(SRC, file)}`);
    continue;
  }

  src = src.replace(IMPORT_RE, 'import { Icon } from "@/components/ui/Icon";\n');

  for (const name of names) {
    const key = MAP[name];
    const open = new RegExp(`<${name}(?=[\\s/>])`, "g");
    let hits = 0;
    let out = "";
    let cursor = 0;
    let mm;
    while ((mm = open.exec(src)) !== null) {
      const tagStart = mm.index;
      const end = findTagEnd(src, tagStart + 1);
      if (end < 0) break;
      const tag = src.slice(tagStart, end);
      // Self-closing only; a tag with children would need a different edit.
      if (!tag.endsWith("/>")) {
        report.push(`  ⚠️ ${name}: yopiluvchi teg emas — qo'lda: ${path.relative(SRC, file)}`);
        open.lastIndex = end;
        continue;
      }
      const attrs = tag.slice(1 + name.length, -2);
      const cls = extractClassName(attrs);
      const replacement = cls
        ? `<Icon name="${key}" className=${cls} />`
        : `<Icon name="${key}" />`;
      out += src.slice(cursor, tagStart) + replacement;
      cursor = end;
      hits++;
      open.lastIndex = end;
    }
    if (hits) {
      out += src.slice(cursor);
      src = out;
      perIcon[key] = (perIcon[key] ?? 0) + hits;
    }
  }

  fs.writeFileSync(file, src);
  filesChanged++;
}

console.log(`O'zgartirilgan fayl: ${filesChanged}`);
const total = Object.values(perIcon).reduce((a, b) => a + b, 0);
console.log(`Almashtirilgan ikonka: ${total} (${Object.keys(perIcon).length} xil kalit)`);
console.log("\nKalit bo'yicha:");
for (const [k, n] of Object.entries(perIcon).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(n).padStart(2)}  ${k}`);
}
if (report.length) {
  console.log("\nDiqqat:");
  report.forEach((r) => console.log("  " + r));
}
