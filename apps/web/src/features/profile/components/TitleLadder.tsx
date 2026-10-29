import { TitleIcon } from "@/components/ui/Identity";
import { fill, t, type Locale } from "@/i18n/messages";
import { TITLE_BLOCKS, TITLE_LADDER, nextTier, tierOf, type TitleTier } from "@/lib/title-ladder";
import { RankTitle } from "./RankTitle";
import type { TitleBand, UserTitle } from "@/lib/identity";

/** Where the user stands on the 16-tier ladder (ADR-0027).
 *
 *  A title name does not say what comes next (is Pulsar above Comet?), so the
 *  ladder is spelled out: tiers grouped into blocks, highest first, with the
 *  current one marked and the distance to the next. The summary line is
 *  always visible; the full ladder opens on demand, so the profile does not
 *  grow by 16 rows for everyone.
 *
 *  Bounds come from the API (`bands`); the code order and the blocks come
 *  from `lib/title-ladder.ts`. Icons move here and nowhere else in a list. */
export function TitleLadder({
  title,
  bands,
  rating,
  locale,
}: {
  title: UserTitle | null;
  bands: TitleBand[];
  rating: number | null;
  locale: Locale;
}) {
  const marker = (code: string) => bands.find((band) => band.code === code)?.marker ?? 0;
  const group = (code: string) => bands.find((band) => band.code === code)?.colour_group ?? "grey";
  const current = title ? tierOf(title.code) : undefined;
  const next = title ? nextTier(title.code) : undefined;
  const toNext = next && rating !== null ? Math.max(next.min - rating, 0) : null;
  const span = current && next ? next.min - current.min : 0;
  const done = current && rating !== null && span > 0 ? Math.min(Math.max((rating - current.min) / span, 0), 1) : 0;

  const row = (tier: TitleTier) => {
    const here = tier.code === title?.code;
    const upper = TITLE_LADDER[tier.level];
    return (
      <li
        key={tier.code}
        aria-current={here ? "true" : undefined}
        className={`flex items-center gap-3 rounded-lg px-3 py-1.5 rw-rank-${group(tier.code)} ${here ? "rw-accent-soft" : ""}`}
      >
        <TitleIcon code={tier.code} live className="size-9" />
        <span className="min-w-0 flex-1">
          <span className="block text-theme-sm font-semibold">
            <RankTitle locale={locale} code={tier.code} marker={marker(tier.code)} />
          </span>
          <span className="block rw-dim text-theme-xs tabular-nums">
            {tier.min}
            {upper ? `–${upper.min - 1}` : "+"}
          </span>
        </span>
        {here && (
          <span className="rounded-full border border-current px-2 py-0.5 text-theme-xs font-semibold">
            {t(locale, "title.ladder.current")}
          </span>
        )}
      </li>
    );
  };

  return (
    <details className="group rounded-lg border rw-line">
      <summary className="flex min-h-11 cursor-pointer list-none flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 [&::-webkit-details-marker]:hidden">
        {title && current ? (
          <>
            <span className={`flex items-center gap-3 rw-rank-${title.colour_group}`}>
              <TitleIcon code={title.code} live className="size-14" />
              <span className="text-theme-lg font-bold">
                <RankTitle locale={locale} code={title.code} marker={title.marker} />
              </span>
            </span>
            <span className="min-w-0 flex-1 basis-48 space-y-1.5">
              <span className="block text-theme-xs rw-dim">
                {[
                  fill(t(locale, "title.ladder.position"), { level: current.level, total: TITLE_LADDER.length }),
                  next && toNext !== null
                    ? fill(t(locale, "title.ladder.progress"), { points: toNext, next: t(locale, `title.${next.code}`) })
                    : !next
                      ? t(locale, "title.ladder.top")
                      : null,
                ]
                  .filter(Boolean)
                  .join(" · ")}
              </span>
              {next && rating !== null && (
                <span
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(done * 100)}
                  aria-label={t(locale, "title.ladder.heading")}
                  className="block h-1.5 overflow-hidden rounded-full rw-chip"
                >
                  <span
                    className={`block h-full rounded-full bg-current rw-rank-${title.colour_group}`}
                    style={{ width: `${Math.round(done * 100)}%` }}
                  />
                </span>
              )}
            </span>
          </>
        ) : (
          <span className="text-theme-sm rw-dim">{t(locale, "title.ladder.none")}</span>
        )}
        <span className="text-theme-xs font-medium rw-accent-ink group-open:hidden">
          {fill(t(locale, "title.ladder.showAll"), { total: TITLE_LADDER.length })}
        </span>
        <span className="hidden text-theme-xs font-medium rw-accent-ink group-open:inline">
          {t(locale, "title.ladder.hide")}
        </span>
      </summary>
      <div className="space-y-4 border-t rw-line px-2 py-3">
        {[...TITLE_BLOCKS].reverse().map((block) => {
          const tiers = TITLE_LADDER.filter((tier) => tier.block === block).reverse();
          return (
            <section key={block} aria-labelledby={`ladder-${block}`}>
              <h3 id={`ladder-${block}`} className="px-3 pb-1 text-theme-xs font-semibold uppercase tracking-wide rw-dim">
                {t(locale, `title.block.${block}`)}
              </h3>
              <ol className="space-y-0.5">{tiers.map(row)}</ol>
            </section>
          );
        })}
      </div>
    </details>
  );
}
