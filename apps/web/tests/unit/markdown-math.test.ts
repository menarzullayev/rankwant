import { readFileSync } from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Markdown } from "@/components/ui/Markdown";

const LOCK = new URL("../../../../package-lock.json", import.meta.url);

const render = (text: string) =>
  renderToStaticMarkup(createElement(Markdown, null, text));

describe("Markdown formulas", () => {
  it("renders inline and display maths", () => {
    const html = render(
      "Inline $a^2+b^2=c^2$ and\n\n$$\n\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}\n$$\n",
    );
    expect(html.match(/class="katex"/g)?.length).toBe(2);
    expect(html).toContain("katex-display");
    expect(html).not.toContain("katex-error");
  });

  it("shows a broken formula as an error, not as an exception", () => {
    expect(render("bad $\\frac{1$")).toContain("katex-error");
  });

  // Statements are written by problem setters; raw HTML must stay text.
  it("does not pass raw HTML through", () => {
    expect(render("<img src=x onerror=alert(1)>")).not.toContain("<img");
  });
});

// `rehype-katex` and `remark-math` ask for katex ^0.16; the stylesheet the
// page imports is the app's own katex. Two copies mean markup from one
// release styled by another, and the nested one stays on a version with a
// published advisory. The root `overrides` keep it to one — npm reads that
// block only from the workspace root, so this is what notices it moving back.
describe("package-lock", () => {
  const packages = Object.entries(
    (JSON.parse(readFileSync(LOCK, "utf8")) as {
      packages: Record<string, { version?: string }>;
    }).packages,
  );
  const copies = (name: string) =>
    packages.filter(([path]) => path.endsWith(`node_modules/${name}`));

  it("holds one katex", () => {
    expect(copies("katex").map(([path]) => path)).toEqual(["node_modules/katex"]);
  });

  it("holds one dompurify, past the advisories fixed in 3.4.16", () => {
    const found = copies("dompurify");
    expect(found.map(([path]) => path)).toEqual(["node_modules/dompurify"]);
    const [major, minor, patch] = (found[0]?.[1].version ?? "0.0.0").split(".").map(Number);
    expect(major * 1e6 + minor * 1e3 + patch).toBeGreaterThanOrEqual(3_004_016);
  });
});
