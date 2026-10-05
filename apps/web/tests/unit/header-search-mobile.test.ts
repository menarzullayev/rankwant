import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const search = src("../../src/layout/SearchBox.tsx");

describe("H3 mobile search-icon", () => {
  it("is a magnifier button below md and a field-shaped button from md up", () => {
    // One button at every width: typing happens in the palette, so there
    // is no hidden field to reveal and nothing to position on a phone.
    expect(search).toContain("flex size-10 shrink-0");
    expect(search).toContain("md:w-36");
    expect(search).toContain("hidden min-w-0 flex-1 truncate");
    expect(search).toContain('aria-keyshortcuts="Control+K Meta+K"');
    expect(search).toContain('aria-haspopup="dialog"');
    expect(search).toContain("aria-expanded={open}");
    expect(search).not.toMatch(/w-64/);
    expect(search).not.toContain("<input");
    expect(search).toContain('className="pointer-events-none size-5 shrink-0"');
  });

  it("makes the palette a full-height sheet on a phone", () => {
    const palette = src("../../src/components/search/SearchPalette.tsx");
    expect(palette).toContain("flex h-dvh w-full flex-col");
    expect(palette).toContain("sm:h-auto");
    expect(palette).toContain("[@media(pointer:coarse)]:h-11");
    expect(palette).toContain("min-h-11");
  });
});
