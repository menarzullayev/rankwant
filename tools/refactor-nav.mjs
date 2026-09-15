// Refactor layout/nav.ts so the Icon field becomes an iconKey string looked up
// from the registry by consumers. This lets the sidebar/topnav icons follow
// the chosen pack, which is the whole point of the registry — without it, the
// sidebar would always render the hand-drawn style and the user would think
// nothing happened when they switched packs.
//
// The mapping below maps each nav item's old icon component to the most
// fitting semantic key. Where the inventory already had an exact `nav.*` key
// (problems, leaderboard, quiz, shop), it is used; otherwise a domain key
// (content.article for the blog, ranking.trophy for contests, etc.) — the
// goal is that the chosen glyph still says "this is the blog section", not
// that it always matches the page that lives at the href.
import fs from "node:fs";

const FILE = "C:/Users/nsn/project/cp/rankwant/apps/web/src/layout/nav.ts";
let s = fs.readFileSync(FILE, "utf8");

/** Old component name -> iconKey (semantic key, D18). */
const MAP = {
  AlgorithmIcon: "content.algorithm",
  ArenaIcon: "contest.arena",
  AttemptsIcon: "ranking.chartBar",
  BlogIcon: "content.article",
  CalendarIcon: "contest.calendar",
  ClassroomIcon: "content.course",
  ContestIcon: "ranking.trophy",
  DuelIcon: "contest.duel",
  FormulaIcon: "stats.chartBar",
  HackathonIcon: "contest.hackathon",
  InfoIcon: "status.info",
  LeaderboardIcon: "nav.leaderboard",
  LearnIcon: "content.course",
  ProblemsIcon: "nav.problems",
  QuizIcon: "nav.quiz",
  RoadmapIcon: "content.roadmap",
  ShopIcon: "shop.store",
  TeamIcon: "user.group",
  TournamentIcon: "ranking.trophy",
  UpdatesIcon: "notification.changelog",
};

let replaced = 0;
for (const [name, key] of Object.entries(MAP)) {
  // The actual file has `Icon: Name },` — no comma right after Name. We match
  // the identifier alone and rely on \b to keep `IconName` from matching.
  const re = new RegExp(`Icon: ${name}\\b`, "g");
  const n = (s.match(re) ?? []).length;
  s = s.replace(re, `iconKey: "${key}"`);
  replaced += n;
}

// Drop the entire icon import (its only use was the Icon refs we just
// replaced). Match the multi-line block up to the closing `from "@/icons";`.
const importBlock = s.match(/^import \{[\s\S]*?\} from "@\/icons";\r?\n/m);
if (importBlock) s = s.replace(importBlock[0], "");

// Update the NavItem type: Icon (component) -> iconKey (string).
s = s.replace(
  /\bIcon:\s*\(props:\s*\{[^}]*\}\)\s*=>\s*React\.JSX\.Element;/,
  "iconKey: string;",
);

fs.writeFileSync(FILE, s);
console.log(`Icon -> iconKey: ${replaced} o'rin`);