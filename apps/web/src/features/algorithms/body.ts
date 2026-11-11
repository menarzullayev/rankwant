/** How an imported article's text is shown (ADR-0062). The stored text stays
 *  as reviewed; these only decide what the page draws twice. */

const TITLE_LINE = /^#\s[^\n]*\n+/;
const HEADING = /^(#{1,6})\s.*$/;
const PRACTICE_ID = "{#practice-problems}";

/** The text without its own `# Title` line — the page already shows it. */
export function withoutTitle(body: string): string {
  return body.replace(TITLE_LINE, "");
}

/** The text without its "Practice problems" section, whose links the page
 *  shows as a list of its own ("on other sites"). The section is found by
 *  the original's heading id; code blocks are skipped, and the section ends
 *  at the next heading of the same or a higher level. */
export function withoutPracticeSection(body: string): string {
  const lines = body.split("\n");
  let inCode = false;
  let start = -1;
  let level = 0;
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (/^\s*(```|~~~)/.test(line)) inCode = !inCode;
    if (inCode) continue;
    const head = HEADING.exec(line);
    if (!head) continue;
    if (start === -1 && line.trimEnd().endsWith(PRACTICE_ID)) {
      start = i;
      level = head[1].length;
    } else if (start !== -1 && head[1].length <= level) {
      return [...lines.slice(0, start), ...lines.slice(i)].join("\n");
    }
  }
  return start === -1 ? body : lines.slice(0, start).join("\n").trimEnd() + "\n";
}
