import type { ReactNode } from "react";

import { t, type Locale } from "@/i18n/messages";

/** Render a tier name with its nutella marker (ADR-0027 § L2).

The first `marker` characters are drawn in `--rw-nutella-ink` (black on
light surfaces, white on dark), the rest stays in the parent's
`--rw-rank-N` colour. The parent must already apply the rank class so
the bulk of the name has the tier colour; this component only paints
the head in the ink colour.

Use inside an element that already has `class="rw-rank-{level}"`:

    <span className="rw-rank-16">
      <RankTitle locale={locale} code={title.code} marker={title.marker} />
    </span>
*/

export function RankTitle({
  locale,
  code,
  marker,
}: {
  locale: Locale;
  code: string;
  marker: number;
}): ReactNode {
  const text = t(locale, `title.${code}`);
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
