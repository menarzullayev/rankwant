import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Markdown } from "@/components/ui/Markdown";

const render = (text: string, anchors: boolean, lang = "en") =>
  // `Markdown` has no hooks, so it can be called as a function here.
  renderToStaticMarkup(Markdown({ anchors, lang, children: text }));

// The algorithms library writes section ids as `{#id}` after a heading, and
// links point at them (ADR-0062).
describe("Markdown heading anchors", () => {
  it("turns a trailing {#id} into the heading's id", () => {
    const html = render("## Implementation {#implementation}\n\ntext", true);
    expect(html).toContain('<h2 id="implementation">Implementation</h2>');
  });

  it("leaves other texts as they were", () => {
    expect(render("## Implementation {#implementation}", false)).toContain("{#implementation}");
  });

  it("keeps the id as written under the Uzbek alphabet conversion", () => {
    const html = render("## Qidiruv {#search-chain}", true, "uz");
    expect(html).toContain('id="search-chain"');
  });
});
