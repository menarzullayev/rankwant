import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import {
  filterLocal,
  foldText,
  highlight,
  hitHref,
  isAskable,
  parseQuery,
  rankLocal,
  sameHit,
  searchHref,
  SERVER_TYPES,
  type SearchHit,
} from "../../src/lib/search/model";
import { pushRecent, RECENT_LIMIT } from "../../src/lib/search/recent";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const hit = (over: Partial<SearchHit>): SearchHit => ({
  type: "problem",
  kind: "problem",
  key: "a-plus-b",
  title: "A+B",
  ...over,
});

describe("search folding", () => {
  it("drops every apostrophe form, case and extra spaces", () => {
    for (const mark of ["'", "’", "ʻ", "‘", "`", "´"]) {
      expect(foldText(`Bo${mark}lish`)).toBe("bolish");
    }
    expect(foldText("  Ikki   SO'Z ")).toBe("ikki soz");
  });

  it("strips the same characters the server does", () => {
    const server = src("../../../api/core/search.py");
    const line = server.split("\n").find((row) => row.startsWith("APOSTROPHES = "));
    expect(line).toBe(`APOSTROPHES = "'’ʻ‘\`´"`);
  });

  it("serves the same result types the server registers", () => {
    const server = src("../../../api/core/search.py");
    expect(server).toContain(`TYPES = (${SERVER_TYPES.map((name) => `"${name}"`).join(", ")})`);
  });
});

describe("search highlighting", () => {
  it("marks the match in the original text, not in the folded one", () => {
    expect(highlight("Yig'indi", "yigin")).toEqual([
      { text: "Yig'in", hit: true },
      { text: "di", hit: false },
    ]);
  });

  it("marks every occurrence", () => {
    expect(highlight("Graf va graflar", "graf").filter((part) => part.hit)).toHaveLength(2);
  });

  it("leaves the text whole when nothing matches", () => {
    expect(highlight("Algoritm asoslari", "algortm")).toEqual([
      { text: "Algoritm asoslari", hit: false },
    ]);
    expect(highlight("Reyting", "")).toEqual([{ text: "Reyting", hit: false }]);
  });
});

describe("local ranking", () => {
  it("orders exact, prefix, word start, inside", () => {
    expect(rankLocal("Graf", "graf")).toBe(0);
    expect(rankLocal("Grafda yurish", "graf")).toBe(1);
    expect(rankLocal("Katta graflar", "graf")).toBe(2);
    expect(rankLocal("Paragraf", "graf")).toBe(3);
    expect(rankLocal("Daraxt", "graf")).toBe(-1);
  });

  it("keeps the given order between equals", () => {
    const items = [{ label: "Reyting formulasi" }, { label: "Reyting" }, { label: "Reyting jadvali" }];
    expect(filterLocal(items, "reyting").map((item) => item.label)).toEqual([
      "Reyting",
      "Reyting formulasi",
      "Reyting jadvali",
    ]);
  });
});

describe("query prefixes", () => {
  it("lets a leading character pick the type", () => {
    expect(parseQuery("@ali", "all")).toEqual({ query: "ali", type: "user", prefixed: true });
    expect(parseQuery("#graf", "problem")).toEqual({ query: "graf", type: "topic", prefixed: true });
    expect(parseQuery(">mavzu", "all")).toEqual({ query: "mavzu", type: "cmd", prefixed: true });
  });

  it("reads #12 as a problem number, not as the topic prefix", () => {
    expect(parseQuery("#12", "all")).toEqual({ query: "#12", type: "all", prefixed: false });
    expect(parseQuery("#dp", "all").type).toBe("topic");
  });

  it("otherwise keeps the chip", () => {
    expect(parseQuery(" dp ", "learn")).toEqual({ query: "dp", type: "learn", prefixed: false });
  });
});

describe("result links", () => {
  it("sends every kind to its own page", () => {
    expect(hitHref(hit({}))).toBe("/problems/a-plus-b");
    expect(hitHref(hit({ type: "user", kind: "user", key: "ali_dev" }))).toBe("/users/ali_dev");
    expect(hitHref(hit({ type: "topic", kind: "topic", key: "dp" }))).toBe("/problems?topics=dp");
    expect(hitHref(hit({ type: "contest", kind: "contest", key: "r1" }))).toBe("/contests/r1");
    expect(hitHref(hit({ type: "contest", kind: "arena", key: "r1" }))).toBe("/arena/r1");
    expect(hitHref(hit({ type: "contest", kind: "tournament", key: "r1" }))).toBe("/tournaments/r1");
    expect(hitHref(hit({ type: "contest", kind: "hackathon", key: "r1" }))).toBe("/hackathons/r1");
    expect(hitHref(hit({ type: "learn", kind: "article", key: "dp" }))).toBe("/learn/dp");
    expect(hitHref(hit({ type: "learn", kind: "algorithm", key: "bfs" }))).toBe("/learn/bfs");
    expect(hitHref(hit({ type: "learn", kind: "quiz", key: "q1" }))).toBe("/quizzes/q1");
    expect(hitHref(hit({ type: "learn", kind: "roadmap", key: "yol" }))).toBe("/roadmaps#yol");
    expect(hitHref(hit({ type: "news", kind: "post", key: "yangi" }))).toBe("/blog/yangi");
    expect(hitHref(hit({ type: "news", kind: "update", key: "12" }))).toBe("/updates/12");
  });

  it("sends the new kinds to their pages", () => {
    expect(hitHref(hit({ type: "news", kind: "plan", key: "7" }))).toBe("/platform-roadmap/7");
    // A translated title leads to the same entry as the original.
    expect(hitHref(hit({ type: "news", kind: "update_translation", key: "12" }))).toBe("/updates/12");
    expect(hitHref(hit({ type: "shop", kind: "shop_item", key: "oltin-ramka" }))).toBe("/qvant");
  });

  it("asks the server about a one-digit problem number, not about one letter", () => {
    expect(isAskable("7")).toBe(true);
    expect(isAskable("#7")).toBe(true);
    expect(isAskable("t")).toBe(false);
    expect(isAskable("#")).toBe(false);
    expect(isAskable("dp")).toBe(true);
  });

  it("recognises the top hit inside its group", () => {
    const top = hit({ key: "toliq-qism-graf" });
    expect(sameHit(top, hit({ key: "toliq-qism-graf" }))).toBe(true);
    expect(sameHit(top, hit({ key: "boshqa" }))).toBe(false);
    expect(sameHit(top, hit({ type: "user", kind: "user", key: "toliq-qism-graf" }))).toBe(false);
  });

  it("builds the results page address without the defaults", () => {
    expect(searchHref("dp")).toBe("/search?q=dp");
    expect(searchHref("a b", "user", 3)).toBe("/search?q=a+b&type=user&page=3");
    // Pages and commands never leave the browser.
    expect(searchHref("dp", "cmd")).toBe("/search?q=dp");
  });
});

describe("recent searches", () => {
  it("puts the newest first and forgets the older copy", () => {
    expect(pushRecent(["graf", "dp"], "DP")).toEqual(["DP", "graf"]);
  });

  it("keeps a short list and ignores a one-letter query", () => {
    const many = Array.from({ length: RECENT_LIMIT }, (_, index) => `so'rov ${index}`);
    expect(pushRecent(many, "yangi")).toHaveLength(RECENT_LIMIT);
    expect(pushRecent(many, "a")).toBe(many);
  });
});

describe("what the comparison with other platforms added", () => {
  const palette = src("../../src/components/search/SearchPalette.tsx");
  const page = src("../../src/app/(site)/search/page.tsx");
  const describe_ = src("../../src/components/search/describe.ts");

  it("shows the top hit once, above the groups", () => {
    expect(palette).toContain('label: t(locale, "search.top")');
    expect(palette).toContain("group.results.filter((hit) => !sameHit(hit, top))");
    expect(page).toContain("group.results.filter((hit) => !sameHit(hit, top))");
  });

  it("quotes the text a body match was found in", () => {
    expect(describe_).toContain("hit.snippet ? { ...plain, subtitle: hit.snippet, quoted: true }");
    expect(palette).toContain("<Highlight text={option.subtitle} query={query} />");
    expect(page).toContain("<Highlight text={text.subtitle} query={query} />");
  });

  it("says so when the server asks to slow down", () => {
    expect(palette).toContain("response.status === THROTTLED");
    expect(palette).toContain('response.headers.get("Retry-After")');
    expect(page).toContain("error.status === THROTTLED");
    expect(page).toContain('t(locale, "search.throttledWait")');
  });

  it("offers matching sections of the site on the results page too", () => {
    expect(page).toContain("NAV.map((item) => ({ label: t(locale, item.key), href: item.href }))");
  });
});

describe("the one search surface", () => {
  const box = src("../../src/layout/SearchBox.tsx");
  const palette = src("../../src/components/search/SearchPalette.tsx");

  it("opens the palette from the header and from Ctrl+K", () => {
    expect(box).toContain("<SearchPalette onClose={close} />");
    expect(box).toContain('aria-haspopup="dialog"');
    expect(box).not.toContain("/search/?q=");
  });

  it("drives the list from the input", () => {
    expect(palette).toContain('role="combobox"');
    expect(palette).toContain("aria-activedescendant={current?.id}");
    expect(palette).toContain('role="listbox"');
    expect(palette).toContain('role="option"');
    for (const key of ["ArrowDown", "ArrowUp", "Enter", "Tab", "Escape"]) {
      expect(palette).toContain(`case "${key}":`);
    }
  });

  it("reads the results page and the palette from the same describer", () => {
    expect(palette).toContain("describeHit(hit, locale)");
    expect(src("../../src/app/(site)/search/page.tsx")).toContain("describeHit(hit, locale)");
  });
});
