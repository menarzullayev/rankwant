import { fill, t, type Locale } from "@/i18n/messages";

/** How much of a study plan or one of its sections the reader has solved
 *  (ADR-0060 § 2.4). A guest sees the step count with nothing solved. */
export function Progress({
  solved,
  total,
  label,
  locale,
}: {
  solved: number;
  total: number;
  label: string;
  locale: Locale;
}) {
  const percent = total > 0 ? Math.round((solved / total) * 100) : 0;
  return (
    <div>
      <p className="text-theme-xs rw-faint tabular-nums">
        {fill(t(locale, "roadmaps.progress"), { solved, total })}
      </p>
      <div
        className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip"
        role="progressbar"
        aria-valuenow={solved}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-label={label}
      >
        <div className="h-full rounded-full rw-accent-bg" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

/** Where a step leads: a problem or an article. */
export function stepHref(step: { problem: string | null; article: string | null }): string | null {
  if (step.problem) return `/problems/${step.problem}`;
  if (step.article) return `/learn/${step.article}`;
  return null;
}
