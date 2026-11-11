import { describe, expect, it } from "vitest";

import { linkTerms } from "@/features/algorithms/glossary";

const entry = (term: string, slug: string, note = `${term} — izoh`) => ({
  slug,
  term,
  english: slug,
  aliases: [],
  note,
});
const GLOSSARY = [entry("Segment daraxti", "segment-tree"), entry("Graf", "graph"), entry("Stek", "stack")];

describe("glossary links in an article", () => {
  it("links the first use of a term, with its note as the title", () => {
    const out = linkTerms("Segment daraxti tez. Segment daraxti yana.", GLOSSARY);
    expect(out).toBe(
      '[Segment daraxti](/algorithms/glossary#segment-tree "Segment daraxti — izoh") tez. Segment daraxti yana.',
    );
  });

  it("takes a term with its Uzbek ending but not a longer word", () => {
    expect(linkTerms("graflarda yo'l", GLOSSARY)).toContain("[graflarda](/algorithms/glossary#graph");
    expect(linkTerms("grafik chizamiz", GLOSSARY)).toBe("grafik chizamiz");
  });

  it("leaves code, formulas, links and headings alone", () => {
    const body = [
      "## Graf haqida",
      "`Graf` va $Graf$ va [Graf](https://x.uz) va ![Graf](/a.png)",
      "```cpp",
      "Graf g; // Stek",
      "```",
    ].join("\n");
    expect(linkTerms(body, GLOSSARY)).toBe(body);
  });

  it("stops at the limit, longest terms first", () => {
    const out = linkTerms("Graf, Stek va Segment daraxti.", GLOSSARY, { limit: 1 });
    expect(out).toContain("[Segment daraxti]");
    expect(out).not.toContain("[Graf]");
  });

  it("keeps a quote out of the title", () => {
    const out = linkTerms("Stek", [entry("Stek", "stack", 'LIFO "oxirgi"')]);
    expect(out).toBe(`[Stek](/algorithms/glossary#stack "LIFO 'oxirgi'")`);
  });
});
