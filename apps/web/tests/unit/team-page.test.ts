import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { initialsOf } from "@/components/team/Person";
import { TEAM_TEXT, localized, pickTeam } from "@/content/team";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const page = src("../../src/app/(site)/team/page.tsx");
const directory = src("../../src/components/team/TeamDirectory.tsx");
const person = src("../../src/components/team/Person.tsx");
const admin = src("../../src/components/admin/TeamAdmin.tsx");

describe("team page", () => {
  it("says the same things in every language it is written in", () => {
    const keys = Object.keys(TEAM_TEXT.uz).sort();
    for (const [code, text] of Object.entries(TEAM_TEXT)) {
      expect(Object.keys(text).sort(), code).toEqual(keys);
      expect(text.stats, code).toHaveLength(4);
      expect(text.detail.length, code).toBe(TEAM_TEXT.uz.detail.length);
      expect(text.count, code).toContain("{roles}");
      expect(text.count, code).toContain("{people}");
      expect(text.photoAlt, code).toContain("{name}");
      expect(text.showMore, code).toContain("{count}");
      expect(text.ownerCardTitle, code).toContain("{name}");
      expect(text.metaTitle, code).toContain("{roles}");
      expect(text.metaDescription, code).toContain("{departments}");
    }
  });

  it("falls back to Uzbek: for a locale it is not written in, and for a blank translation", () => {
    expect(pickTeam("ru")).toBe("ru");
    expect(pickTeam("tr")).toBe("uz");
    const row = { title_uz: "Asoschi", title_ru: "", title_en: "Founder" };
    expect(localized(row, "title", "en")).toBe("Founder");
    expect(localized(row, "title", "ru")).toBe("Asoschi");
    expect(localized({}, "title", "uz")).toBe("");
  });

  it("draws initials for a member without a photo", () => {
    expect(initialsOf("Saidakbar Narzullayev")).toBe("SN");
    expect(initialsOf("  ali  ")).toBe("A");
    expect(initialsOf("Bir Ikki Uch")).toBe("BI");
  });

  it("reads people and titles from the API and counts its header from them", () => {
    expect(page).toContain("api.team()");
    expect(page).toContain(".catch(() => null)");
    expect(page).toContain("roles.length");
    expect(page).not.toContain('"use client"');
    expect(directory).toContain('"use client"');
  });

  it("shows contributors and the serious card as portraits with icon links", () => {
    expect(page).toContain("text.contributorsTitle");
    expect(page).toContain('m.section === "contributor"');
    expect(directory).toContain("<PersonCard member={owner}");
    expect(person).toContain("aria-label={`${label}: ${member.name}`}");
    expect(person).toContain('rel="noopener noreferrer"');
    // No address on the page: Cloudflare would inject its e-mail decoder.
    expect(page + directory + person).not.toContain("mailto:");
  });

  it("is managed from one admin page with three lists", () => {
    for (const path of ["/staff/team/members/", "/staff/team/roles/", "/staff/team/departments/"]) {
      expect(admin).toContain(`path="${path}"`);
    }
    expect(src("../../src/components/admin/sections.ts")).toContain('href: "/admin/team"');
  });
});
