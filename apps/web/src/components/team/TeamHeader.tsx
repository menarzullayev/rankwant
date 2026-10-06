import type { TeamText } from "@/content/team";

/** The page's heading and, in the joke view, its four numbers on one line.
 *
 *  The numbers were four cards (two rows on a phone, 190 px); they are a
 *  punchline, not a dashboard, and read as well in a sentence. `stats` is
 *  `null` where they do not belong: the serious view, and a page whose
 *  list could not be loaded. The heading takes focus when the view
 *  changes under it, hence `tabIndex`. */
export function TeamHeader({
  text,
  heading,
  lede,
  stats,
}: {
  text: TeamText;
  heading: string;
  lede: string;
  stats: readonly number[] | null;
}) {
  return (
    <header className="space-y-3">
      <p className="font-mono text-theme-xs tracking-wide rw-accent-ink uppercase">{text.eyebrow}</p>
      <h1
        tabIndex={-1}
        className="max-w-[18ch] text-title-md leading-tight font-bold text-balance rw-strong outline-none"
      >
        {heading}
      </h1>
      <p className="max-w-prose text-theme-base rw-dim">{lede}</p>
      {stats ? (
        <dl className="flex flex-wrap gap-x-4 gap-y-1 text-theme-sm rw-dim">
          {stats.map((value, index) => (
            <div key={text.stats[index]} className="flex items-baseline gap-1.5">
              <dt className="order-last">{text.stats[index]}</dt>
              <dd className="text-theme-base font-bold rw-strong tabular-nums">{value}</dd>
            </div>
          ))}
        </dl>
      ) : null}
    </header>
  );
}
