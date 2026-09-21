import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const search = src("../../src/layout/SearchBox.tsx");

describe("H3 mobile search-icon", () => {
  it("shows a lupa trigger below md and keeps the field on md+", () => {
    expect(search).toContain('aria-controls="rw-header-search"');
    expect(search).toContain("md:hidden");
    expect(search).toContain("id=\"rw-header-search\"");
    expect(search).toContain("md:block");
    expect(search).toContain("setExpanded(true)");
    expect(search).toContain('aria-keyshortcuts="Control+K Meta+K"');
    expect(search).toContain("w-full max-w-full");
    expect(search).not.toMatch(/w-64/);
    expect(search).toContain("fixed inset-x-3");
    expect(search).not.toContain("} relative md:block");
    expect(search).toContain('className="pointer-events-none"');
  });
});
