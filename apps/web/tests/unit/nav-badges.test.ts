import { describe, expect, it } from "vitest";

import {
  SEEN_ON_VISIT,
  badgeText,
  sectionOf,
  toBadgeMap,
} from "@/lib/nav-badges";

describe("sectionOf", () => {
  it("reads the list page of a section", () => {
    expect(sectionOf("/blog")).toBe("blog");
    expect(sectionOf("/platform-roadmap/")).toBe("platform-roadmap");
  });

  it("does not take a page inside the section for the section", () => {
    // Reading one post does not mean the other new posts were seen.
    expect(sectionOf("/blog/first-post")).toBeNull();
    expect(sectionOf("/problems/a-plus-b/status")).toBeNull();
    expect(sectionOf("/")).toBeNull();
  });
});

describe("toBadgeMap", () => {
  it("keys the rows by menu path", () => {
    expect(
      toBadgeMap(
        [
          { section: "duels", kind: "todo", count: 1 },
          { section: "contests", kind: "live", count: 2 },
        ],
        0,
      ),
    ).toEqual({
      "/duels": { kind: "todo", count: 1 },
      "/contests": { kind: "live", count: 2 },
    });
  });

  it("adds the changelog's own count as an unread badge", () => {
    expect(toBadgeMap([], 4)).toEqual({
      "/updates": { kind: "unread", count: 4 },
    });
    expect(toBadgeMap([], 0)).toEqual({});
  });

  it("drops a kind it does not know and a count of nothing", () => {
    expect(
      toBadgeMap(
        [
          { section: "shop", kind: "sale", count: 3 },
          { section: "blog", kind: "unread", count: 0 },
        ],
        0,
      ),
    ).toEqual({});
  });
});

describe("badgeText", () => {
  it("caps a large count", () => {
    expect(badgeText(7)).toBe("7");
    expect(badgeText(99)).toBe("99");
    expect(badgeText(100)).toBe("99+");
  });
});

describe("SEEN_ON_VISIT", () => {
  it("never clears work or a live event by looking at it", () => {
    for (const section of ["duels", "classroom", "contests", "arena"]) {
      expect(SEEN_ON_VISIT.has(section)).toBe(false);
    }
  });
});
