import { describe, expect, it } from "vitest";

import { ALL_DEPARTMENTS, readTeamView, teamHref } from "@/components/team/state";

const DEPARTMENTS = [1, 2, 3];

describe("readTeamView", () => {
  it("reads a shared address", () => {
    expect(readTeamView({ dept: "2", q: "kod" }, DEPARTMENTS)).toEqual({
      dept: 2,
      query: "kod",
      serious: false,
    });
    expect(readTeamView({ view: "serious" }, DEPARTMENTS).serious).toBe(true);
  });

  it("falls back to the whole list for anything it cannot read", () => {
    // The address is typed and shared by hand: a wrong value is never an error.
    for (const dept of ["999", "abc", "1.5", "", undefined]) {
      expect(readTeamView({ dept }, DEPARTMENTS).dept).toBe(ALL_DEPARTMENTS);
    }
    expect(readTeamView({ view: "nope" }, DEPARTMENTS).serious).toBe(false);
    expect(readTeamView({ q: ["a", "b"] }, DEPARTMENTS).query).toBe("a");
  });

  it("does not carry an endless query into the page", () => {
    expect(readTeamView({ q: "x".repeat(500) }, DEPARTMENTS).query).toHaveLength(60);
  });
});

describe("teamHref", () => {
  it("is the bare path for the default view", () => {
    expect(teamHref({ dept: ALL_DEPARTMENTS, query: "  ", serious: false })).toBe("/team");
  });

  it("writes the filter and the search", () => {
    expect(teamHref({ dept: 2, query: "bosh dizayner", serious: false })).toBe(
      "/team?dept=2&q=bosh+dizayner",
    );
  });

  it("carries no filter into the serious view, which has none", () => {
    expect(teamHref({ dept: 2, query: "kod", serious: true })).toBe("/team?view=serious");
  });

  it("round-trips through the reader", () => {
    const view = { dept: 3, query: "ux", serious: false };
    const params = Object.fromEntries(new URL(teamHref(view), "https://x").searchParams);
    expect(readTeamView(params, DEPARTMENTS)).toEqual(view);
  });
});
