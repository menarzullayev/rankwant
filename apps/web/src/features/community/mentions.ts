/** Mentions in a comment (decision 2026-11-11 ⑧): a pure module, so it is unit-tested. */

/** `@name` becomes a profile link, outside code (fenced or inline). */
export function linkMentions(text: string): string {
  let fenced = false;
  return text
    .split("\n")
    .map((line) => {
      if (/^\s{0,3}(`{3,}|~{3,})/.test(line)) {
        fenced = !fenced;
        return line;
      }
      if (fenced) return line;
      return line
        .split("`")
        .map((part, i) =>
          i % 2 === 1
            ? part
            : part.replace(
                /(^|[\s(])@([A-Za-z0-9_][A-Za-z0-9_.-]{2,31})/g,
                "$1[@$2](/users/$2)",
              ),
        )
        .join("`");
    })
    .join("\n");
}
