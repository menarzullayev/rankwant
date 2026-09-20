import type { ReactNode } from "react";

/** Render `text` with the first `marker` characters drawn in
 *  `--rw-nutella-ink` (black on light surfaces, white on dark), the rest
 *  in the parent's inherited colour. ADR-0027 § L2.
 *
 *  Use inside an element that already has the tier-colour class
 *  (`rw-rank-{level}`):
 *
 *    <span className="rw-rank-16">
 *      <MarkerText text={username} marker={title.marker} />
 *    </span>
 *
 *  When `marker` is 0 or >= text.length the whole text is returned as a
 *  plain string - no wrapper span - so the caller can use the result
 *  anywhere a string is expected.
 */
export function MarkerText({
  text,
  marker,
}: {
  text: string;
  marker: number;
}): ReactNode {
  if (marker <= 0 || marker >= text.length) {
    return text;
  }
  return (
    <>
      <span style={{ color: "var(--rw-nutella-ink)" }}>{text.slice(0, marker)}</span>
      {text.slice(marker)}
    </>
  );
}
