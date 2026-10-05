import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { TEAM_MEMBER, TEAM_ROLES, TEAM_TEXT, pickTeam } from "@/content/team";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const page = src("../../src/app/(site)/team/page.tsx");
const directory = src("../../src/components/team/TeamDirectory.tsx");

describe("team page", () => {
  it("has the same roles and departments in every language it is written in", () => {
    for (const [code, text] of Object.entries(TEAM_TEXT)) {
      expect(text.roles, code).toHaveLength(TEAM_ROLES.length);
      expect(text.depts, code).toHaveLength(12);
      expect(text.stats, code).toHaveLength(4);
      for (const role of text.roles) {
        expect(role, code).toHaveLength(4);
        for (const part of role) expect(part.trim(), code).not.toBe("");
      }
      expect(text.count, code).toContain("{roles}");
      expect(text.count, code).toContain("{people}");
      expect(text.photoAlt, code).toContain("{name}");
    }
  });

  it("gives every department at least one role and no role an unknown department", () => {
    const depts = TEAM_TEXT.uz.depts.length;
    for (let index = 0; index < depts; index += 1) {
      expect(TEAM_ROLES.some((role) => role.dept === index), `dept ${index}`).toBe(true);
    }
    for (const role of TEAM_ROLES) {
      expect(role.dept).toBeGreaterThanOrEqual(0);
      expect(role.dept).toBeLessThan(depts);
    }
  });

  it("falls back to Uzbek for a locale the content is not written in", () => {
    expect(pickTeam("ru")).toBe("ru");
    expect(pickTeam("en")).toBe("en");
    expect(pickTeam("tr")).toBe("uz");
    expect(pickTeam("nope")).toBe("uz");
  });

  it("names one person and links only to the project's public addresses", () => {
    expect(TEAM_MEMBER.links.map((link) => link.href)).toEqual([
      "https://t.me/rankwant",
      "https://github.com/menarzullayev",
    ]);
    // No address on the page: Cloudflare would inject its e-mail decoder.
    expect(page + directory).not.toContain("mailto:");
    expect(page + directory).not.toMatch(/@rankwant\.uz/);
  });

  it("counts the header numbers from the data and keeps the page server-rendered", () => {
    expect(page).toContain("TEAM_ROLES.length");
    expect(page).toContain("text.depts.length");
    expect(page).not.toContain('"use client"');
    expect(directory).toContain('"use client"');
    expect(directory).toContain("aria-pressed");
    expect(directory).toContain("aria-expanded");
  });
});
