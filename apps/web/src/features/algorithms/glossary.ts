/** Glossary links inside an article (ADR-0062 § 3: a page and tooltips).
 *
 *  The first use of a glossary term in the text becomes a link to its entry,
 *  with the short note as the link's title — the tooltip. Code, formulas,
 *  links, images and headings are left alone, and an article gets at most a
 *  handful of links: longer (more specific) terms first. */

import type { GlossaryEntry } from "@/lib/api";

/** Uzbek case and plural endings a term may carry in running text. */
const SUFFIX =
  "(?:larining|larning|laridan|larida|lariga|larini|lardan|larda|larga|larni|lari|lar|ining|idan|ida|iga|ini|ning|dagi|dan|ga|da|ni|si|i)?";
const PROTECT = /```[\s\S]*?```|~~~[\s\S]*?~~~|\$\$[\s\S]*?\$\$|\$[^$\n]+\$|`[^`\n]+`|!?\[[^\]]*\]\([^)]*\)|<[^>\n]+>|https?:\/\/\S+|^#{1,6}\s[^\n]*$/gm;

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export const GLOSSARY_PATH = "/algorithms/glossary";

export function linkTerms(
  body: string,
  entries: GlossaryEntry[],
  options: { limit?: number; note?: (text: string) => string } = {},
): string {
  const { limit = 10, note = (text) => text } = options;
  const kept: string[] = [];
  const hold = (text: string) => {
    kept.push(text);
    return `\u0000${kept.length - 1}\u0000`;
  };
  let text = body.replace(PROTECT, hold);
  const terms = entries
    .filter((entry) => entry.note && entry.term.length >= 3)
    .sort((a, b) => b.term.length - a.term.length);
  let linked = 0;
  for (const entry of terms) {
    if (linked >= limit) break;
    const pattern = new RegExp(
      `(?<![\\p{L}\\p{N}\\u0000])${escapeRegExp(entry.term)}${SUFFIX}(?![\\p{L}\\p{N}])`,
      "iu",
    );
    const match = pattern.exec(text);
    if (!match) continue;
    const title = note(entry.note).replace(/"/g, "'").replace(/\s+/g, " ");
    const link = `[${match[0]}](${GLOSSARY_PATH}#${entry.slug} "${title}")`;
    text = text.slice(0, match.index) + hold(link) + text.slice(match.index + match[0].length);
    linked += 1;
  }
  // Restore in reverse: a held link never contains another hold.
  return text.replace(/\u0000(\d+)\u0000/g, (_, i: string) => kept[Number(i)]);
}
