/** Site search — what the palette and the results page share.
 *
 *  The server (`apps/api/core/search.py`) owns matching and ranking for
 *  everything that lives in the database. Pages and commands live in the
 *  client, so the same folding and the same rank order are repeated here
 *  for them — and for highlighting, which has to find the match the
 *  server found in text the server did not fold for us.
 */

/** Result types the API serves, in chip order. */
export const SERVER_TYPES = [
  "problem",
  "user",
  "topic",
  "contest",
  "learn",
  "news",
  "shop",
] as const;
export type ServerType = (typeof SERVER_TYPES)[number];

/** Types that never leave the browser. */
export const LOCAL_TYPES = ["page", "cmd"] as const;
export type LocalType = (typeof LOCAL_TYPES)[number];

export type SearchType = "all" | ServerType | LocalType;
export const SEARCH_TYPES: SearchType[] = ["all", ...SERVER_TYPES, ...LOCAL_TYPES];

export type SearchHit = {
  type: ServerType;
  kind: string;
  key: string;
  title: string;
  subtitle?: string;
  /** The words around a match that was found only in a long text. */
  snippet?: string;
  title_ru?: string;
  title_en?: string;
  code?: number | null;
  meta?: number;
  date?: string | null;
};

export type SearchGroup = {
  type: ServerType;
  count: number;
  fuzzy: boolean;
  results: SearchHit[];
};

export type SearchResponse = {
  q: string;
  type: "all" | ServerType;
  /** The one result the query names outright (a problem number, an exact
   *  username) — or `null`; never a guess. */
  top: SearchHit | null;
  groups: SearchGroup[];
  counts: Record<ServerType, number>;
  total: number;
};

/** Shortest query the server answers. */
export const MIN_QUERY = 2;

/** Whether the server has anything to say to this query. Two characters
 *  at least — except a number, which names a problem even at one digit. */
export function isAskable(query: string): boolean {
  const folded = foldText(query);
  return folded.length >= MIN_QUERY || /^#?\d+$/.test(folded);
}

export function isServerType(value: string): value is ServerType {
  return (SERVER_TYPES as readonly string[]).includes(value);
}

export function isSearchType(value: string): value is SearchType {
  return (SEARCH_TYPES as string[]).includes(value);
}

/** The same characters `core.search.APOSTROPHES` strips. */
const APOSTROPHES = new Set(["'", "’", "ʻ", "‘", "`", "´"]);

/** Folded text plus, for every folded character, where it came from. */
function foldWithMap(text: string): { folded: string; map: number[] } {
  let folded = "";
  const map: number[] = [];
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (APOSTROPHES.has(char)) continue;
    // One source character can lower-case into several (`İ`).
    for (const lower of char.toLowerCase()) {
      folded += lower;
      map.push(index);
    }
  }
  return { folded, map };
}

/** Mirror of `normalize_search`: no apostrophes, lower case, single spaces. */
export function foldText(text: string): string {
  return foldWithMap(text).folded.split(/\s+/).filter(Boolean).join(" ");
}

export type Segment = { text: string; hit: boolean };

/** Splits `text` around every place the folded `needle` occurs in it. */
export function highlight(text: string, query: string): Segment[] {
  const needle = foldText(query);
  if (!needle) return [{ text, hit: false }];
  const { folded, map } = foldWithMap(text);
  const out: Segment[] = [];
  let cursor = 0;
  let from = folded.indexOf(needle);
  while (from !== -1) {
    const start = map[from];
    const end = map[from + needle.length - 1] + 1;
    if (start > cursor) out.push({ text: text.slice(cursor, start), hit: false });
    out.push({ text: text.slice(start, end), hit: true });
    cursor = end;
    from = folded.indexOf(needle, from + needle.length);
  }
  if (cursor < text.length) out.push({ text: text.slice(cursor), hit: false });
  return out.length ? out : [{ text, hit: false }];
}

/** The server's rank order: exact, prefix, word start, inside; -1 is no match. */
export function rankLocal(label: string, query: string): number {
  const needle = foldText(query);
  if (!needle) return 0;
  const folded = foldText(label);
  if (folded === needle) return 0;
  if (folded.startsWith(needle)) return 1;
  if (folded.includes(` ${needle}`)) return 2;
  if (folded.includes(needle)) return 3;
  return -1;
}

/** Keeps the items that match, best first; ties stay in their given order. */
export function filterLocal<T extends { label: string }>(items: T[], query: string): T[] {
  return items
    .map((item, index) => ({ item, index, rank: rankLocal(item.label, query) }))
    .filter((row) => row.rank >= 0)
    .sort((a, b) => a.rank - b.rank || a.index - b.index)
    .map((row) => row.item);
}

/** A leading character that picks a type without touching the chips. */
const PREFIXES: Record<string, SearchType> = { "@": "user", "#": "topic", ">": "cmd" };

export function prefixOf(type: SearchType): string {
  return Object.keys(PREFIXES).find((mark) => PREFIXES[mark] === type) ?? "";
}

export function parseQuery(
  raw: string,
  chip: SearchType,
): { query: string; type: SearchType; prefixed: boolean } {
  // `#12` is a problem's number as it is printed, not the topic "12".
  const scoped = /^#\d+$/.test(raw.trim()) ? undefined : PREFIXES[raw[0] ?? ""];
  if (scoped) return { query: raw.slice(1).trim(), type: scoped, prefixed: true };
  return { query: raw.trim(), type: chip, prefixed: false };
}

/** Where a hit opens. */
export function hitHref(hit: SearchHit): string {
  const key = encodeURIComponent(hit.key);
  switch (hit.type) {
    case "problem":
      return `/problems/${key}`;
    case "user":
      return `/users/${key}`;
    case "topic":
      return `/problems?topics=${key}`;
    case "contest":
      if (hit.kind === "arena") return `/arena/${key}`;
      if (hit.kind === "tournament") return `/tournaments/${key}`;
      if (hit.kind === "hackathon") return `/hackathons/${key}`;
      return `/contests/${key}`;
    case "learn":
      if (hit.kind === "quiz") return `/quizzes/${key}`;
      // Learning paths have one page for all of them.
      if (hit.kind === "roadmap") return `/roadmaps#${key}`;
      return `/learn/${key}`;
    case "news":
      if (hit.kind === "plan") return `/platform-roadmap/${key}`;
      // A translated title leads to the same entry as the original.
      return hit.kind === "post" ? `/blog/${key}` : `/updates/${key}`;
    case "shop":
      // The shop is one page; an item has no address of its own.
      return "/qvant";
  }
}

/** The section a hit belongs to, as an existing navigation key. */
const KIND_LABELS: Record<string, string> = {
  contest: "nav.contests",
  arena: "nav.arena",
  tournament: "nav.tournaments",
  hackathon: "nav.hackathons",
  article: "nav.articles",
  algorithm: "nav.algorithms",
  roadmap: "nav.roadmap",
  quiz: "nav.quizzes",
  post: "nav.blog",
  update: "nav.updates",
  update_translation: "nav.updates",
  plan: "nav.platformRoadmap",
  shop_item: "nav.shop",
};

export function kindLabelKey(hit: SearchHit): string | null {
  return KIND_LABELS[hit.kind] ?? null;
}

const ICONS: Record<string, string> = {
  problem: "nav.problems",
  user: "user.profile",
  topic: "content.algorithm",
  contest: "ranking.trophy",
  arena: "contest.arena",
  tournament: "ranking.trophy",
  hackathon: "contest.hackathon",
  article: "content.course",
  algorithm: "content.algorithm",
  roadmap: "content.roadmap",
  quiz: "nav.quiz",
  post: "content.article",
  update: "notification.changelog",
  update_translation: "notification.changelog",
  plan: "content.roadmap",
  shop_item: "shop.store",
};

export function hitIcon(hit: SearchHit): string {
  return ICONS[hit.kind] ?? ICONS[hit.type] ?? "action.search";
}

/** `/search?q=…&type=…&page=…`, leaving out what is default. */
export function searchHref(query: string, type: SearchType = "all", page = 1): string {
  const params = new URLSearchParams();
  params.set("q", query);
  if (isServerType(type)) params.set("type", type);
  if (page > 1) params.set("page", String(page));
  return `/search?${params.toString()}`;
}

/** Whether two hits are the same thing (the top hit also sits in its group). */
export function sameHit(a: SearchHit, b: SearchHit): boolean {
  return a.type === b.type && a.kind === b.kind && a.key === b.key;
}
