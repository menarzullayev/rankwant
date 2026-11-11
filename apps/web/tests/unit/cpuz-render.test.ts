import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Markdown } from "@/components/ui/Markdown";

// The algorithms library (ADR-0062) renders with the site's own Markdown:
// remark-math + KaTeX. MathJax, which cp-algorithms uses, accepts what KaTeX
// refuses (`eqnarray`, `_` in `\text{}`, `\$` next to a closing `$`), and a
// refused formula reaches the reader as red source text. Measured 2026-11-12:
// 21 of 23 977 formulas did, live. Every article, both languages, must render
// without one.
const LIBRARY = fileURLToPath(new URL("../../../api/content/cpuz/", import.meta.url));

function articles(): string[] {
  const out: string[] = [];
  for (const lang of ["uz", "en"]) {
    const base = join(LIBRARY, lang);
    for (const category of readdirSync(base)) {
      const dir = join(base, category);
      if (!statSync(dir).isDirectory()) continue;
      for (const file of readdirSync(dir)) if (file.endsWith(".md")) out.push(join(dir, file));
    }
  }
  return out;
}

describe("algorithms library renders", () => {
  it("has no formula KaTeX refuses", () => {
    const failed: string[] = [];
    const files = articles();
    for (const path of files) {
      const html = renderToStaticMarkup(Markdown({ children: readFileSync(path, "utf8"), anchors: true, lang: "en" }));
      const errors = html.match(/class="katex-error"[^>]*title="([^"]{0,80})/g) ?? [];
      for (const error of errors) failed.push(`${path.slice(LIBRARY.length)}: ${error}`);
      // A `$$` the parser did not pair reaches the reader as text.
      const prose = html.replace(/<pre[\s\S]*?<\/pre>|<code[\s\S]*?<\/code>|<annotation[\s\S]*?<\/annotation>/g, "");
      if (prose.includes("$$")) failed.push(`${path.slice(LIBRARY.length)}: unpaired $$`);
    }
    expect(files.length).toBe(326);
    expect(failed).toEqual([]);
  }, 120_000);
});
