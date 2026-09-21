import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const search = src("../../src/layout/SearchBox.tsx");
const palette = src("../../src/components/kit/CommandPalette.tsx");
const shell = src("../../src/layout/AppShell.tsx");

describe("H2 Ctrl+K search-owns", () => {
  it("gives Control+K only to SearchBox", () => {
    expect(search).toContain('aria-keyshortcuts="Control+K Meta+K"');
    expect(search).toContain("e.metaKey || e.ctrlKey");
    expect(search).toContain('e.key.toLowerCase() !== "k"');
    expect(palette).not.toContain('toLowerCase() === "k"');
    expect(shell).not.toContain("<CommandPalette");
    expect(shell).not.toContain('from "@/components/kit/CommandPalette"');
  });
});
