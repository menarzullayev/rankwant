import { highlight } from "@/lib/search/model";

/** `text` with the matched part marked — why this result came up.
 *
 *  The mark is a tint of the accent with the text's own colour kept, and
 *  it is also heavier: colour alone would not carry it in every style.
 */
export function Highlight({ text, query }: { text: string; query: string }) {
  return (
    <>
      {highlight(text, query).map((segment, index) =>
        segment.hit ? (
          <mark
            key={index}
            className="rounded-sm bg-[color-mix(in_srgb,var(--rw-accent)_24%,transparent)] font-semibold text-inherit"
          >
            {segment.text}
          </mark>
        ) : (
          <span key={index}>{segment.text}</span>
        ),
      )}
    </>
  );
}
