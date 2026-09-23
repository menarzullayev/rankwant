import type { ReactNode } from "react";

/** Split `text` at the marker boundary: `[head, rest]`.
 *
 *  `head` is drawn in `--rw-nutella-ink`, `rest` keeps the parent's
 *  (tier) colour. ADR-0027 § L2.
 *
 *  - `marker <= 0`      -> `["", text]` — nothing is inked.
 *  - `marker >= length` -> `[text, ""]` — the WHOLE text is inked. A
 *    short handle in a high-marker tier must still carry the signal:
 *    "Alex" at Cosmos (marker 4) is entirely inked, so it does not look
 *    like "Alex" at Magnetar (marker 0, nothing inked).
 *  - otherwise          -> `["tour", "ist"]` for `("tourist", 4)`.
 */
export function splitMarker(text: string, marker: number): [string, string] {
  if (marker <= 0) {
    return ["", text];
  }
  return [text.slice(0, marker), text.slice(marker)];
}

/** Render `text` with the first `marker` characters in nutella ink.
 *
 *  Use inside an element that already has the tier-colour class
 *  (`rw-rank-{level}`):
 *
 *    <span className="rw-rank-16">
 *      <MarkerText text={username} marker={title.marker} />
 *    </span>
 *
 *  With `marker <= 0` the result is a plain string (no wrapper span), so
 *  callers that need a string still work.
 */
export function MarkerText({
  text,
  marker,
}: {
  text: string;
  marker: number;
}): ReactNode {
  const [head, rest] = splitMarker(text, marker);
  if (!head) {
    return rest;
  }
  return (
    <>
      <span style={{ color: "var(--rw-nutella-ink)" }}>{head}</span>
      {rest}
    </>
  );
}
