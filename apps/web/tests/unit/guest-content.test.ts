import { describe, expect, it } from "vitest";

import {
  LIBRARY_ARTICLES,
  POPULAR_PROBLEMS,
  RECENT_CONTESTS,
  libraryArticles,
  popularProblems,
  recentContests,
} from "@/app/(site)/_home/GuestContent";
import type { Article, Contest, Problem } from "@/lib/api";

const problem = (slug: string, tests: boolean) =>
  ({ slug, has_tests: tests, title: slug, locale: "uz", difficulty: 800, code: 1 }) as Problem;

const article = (slug: string, kind: "article" | "algorithm", category: string) =>
  ({ slug, kind, category, title: slug, summary: "", locale: "uz", level: "" }) as Article;

const contest = (slug: string, finished: boolean, end: string) =>
  ({ slug, is_finished: finished, end_at: end, start_at: end, title: slug }) as Contest;

describe("popularProblems", () => {
  it("keeps the order the server gave and drops problems the judge cannot test", () => {
    const list = popularProblems([problem("a", true), problem("b", false), problem("c", true)]);
    expect(list.map((p) => p.slug)).toEqual(["a", "c"]);
  });

  it("shows at most the block's size", () => {
    const many = Array.from({ length: 20 }, (_, i) => problem(`p${i}`, true));
    expect(popularProblems(many)).toHaveLength(POPULAR_PROBLEMS);
  });
});

describe("libraryArticles", () => {
  it("takes algorithm articles that have a library category, not plain articles", () => {
    const list = libraryArticles([
      article("intro", "article", ""),
      article("gcd", "algorithm", "algebra"),
      article("loose", "algorithm", ""),
      article("sieve", "algorithm", "algebra"),
    ]);
    expect(list.map((a) => a.slug)).toEqual(["gcd", "sieve"]);
  });

  it("shows at most the block's size", () => {
    const many = Array.from({ length: 20 }, (_, i) => article(`a${i}`, "algorithm", "algebra"));
    expect(libraryArticles(many)).toHaveLength(LIBRARY_ARTICLES);
  });
});

describe("recentContests", () => {
  it("lists finished contests, the latest first, and skips running or coming ones", () => {
    const list = recentContests([
      contest("old", true, "2026-09-10T10:00:00Z"),
      contest("live", false, "2026-11-20T10:00:00Z"),
      contest("new", true, "2026-10-03T10:00:00Z"),
      contest("mid", true, "2026-09-29T10:00:00Z"),
      contest("oldest", true, "2026-08-01T10:00:00Z"),
    ]);
    expect(list.map((c) => c.slug)).toEqual(["new", "mid", "old"]);
    expect(list).toHaveLength(RECENT_CONTESTS);
  });

  it("is empty when nothing has finished", () => {
    expect(recentContests([contest("live", false, "2026-11-20T10:00:00Z")])).toEqual([]);
  });
});
