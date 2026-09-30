/** Strip a leading markdown heading when it repeats the page title (seed uses `## {title}`). */
export function stripDuplicateStatementHeading(
  markdown: string,
  title: string,
): string {
  const trimmed = markdown.trimStart();
  const match = trimmed.match(/^#{1,6}\s+(.+?)(?:\r?\n|$)/);
  if (!match) return markdown;

  const heading = match[1]
    .replace(/[*_`~[\]()]/g, "")
    .trim()
    .toLowerCase();
  const normalizedTitle = title.trim().toLowerCase();
  if (heading !== normalizedTitle) return markdown;

  return trimmed.slice(match[0].length).trimStart();
}
