import type { ReactNode } from "react";

import { t, type Locale } from "@/i18n/messages";

import { MarkerText } from "@/components/ui/Identity";

/** Render a tier badge with its nutella marker (ADR-0027 § L2).
 *
 *  Look up the localised tier name by `code`, then paint its first
 *  `marker` characters in `--rw-nutella-ink`. The parent's
 *  `rw-rank-{level}` class carries the tier colour for the rest.
 *
 *  Example:
 *
 *    <span className="rw-rank-16">
 *      <RankTitle locale={locale} code="cosmos" marker={4} />
 *    </span>
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
  return <MarkerText text={t(locale, `title.${code}`)} marker={marker} />;
}
