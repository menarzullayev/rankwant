import { Card } from "@/components/ui/Card";
import { fill, t, type Locale } from "@/i18n/messages";
import type { UserStats } from "@/lib/api";
import { SectionHint } from "./SectionHint";

/** Verdikt guruhlari va ranglari — `RE` uch xil yoziladi (eski va yangi). */
const GROUPS: { key: string; verdicts: string[]; color: string }[] = [
  { key: "verdict.AC", verdicts: ["AC"], color: "var(--rw-ok-ink)" },
  { key: "verdict.WA", verdicts: ["WA"], color: "var(--rw-bad-ink)" },
  { key: "verdict.TLE", verdicts: ["TLE"], color: "var(--rw-warn-ink)" },
  {
    key: "verdict.MLE",
    verdicts: ["MLE", "OLE"],
    color: "color-mix(in oklab, var(--rw-warn-ink), var(--rw-bad-ink))",
  },
  {
    key: "verdict.RE",
    verdicts: ["RE", "RE_SIGNAL", "RE_EXIT"],
    color: "color-mix(in oklab, var(--rw-bad-ink) 55%, var(--rw-accent-ink))",
  },
  { key: "verdict.CE", verdicts: ["CE", "COMPILE_TIMEOUT"], color: "var(--rw-accent-ink)" },
];

function VerdictDonut({ stats, locale }: { stats: UserStats; locale: Locale }) {
  const counts = new Map(stats.verdicts.map((row) => [row.verdict, row.count]));
  const known = new Set(GROUPS.flatMap((group) => group.verdicts));
  const slices = [
    ...GROUPS.map((group) => ({
      label: t(locale, group.key),
      color: group.color,
      value: group.verdicts.reduce((sum, v) => sum + (counts.get(v) ?? 0), 0),
    })),
    {
      label: t(locale, "profile.verdictOther"),
      color: "var(--rw-faint)",
      value: stats.verdicts
        .filter((row) => !known.has(row.verdict))
        .reduce((sum, row) => sum + row.count, 0),
    },
  ].filter((slice) => slice.value > 0);
  const total = stats.attempts;
  if (total === 0) return <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>;

  // Aylana uzunligi 100 — `stroke-dasharray` foizda yoziladi.
  let offset = 25;
  const rate = Math.round((stats.accepted / total) * 100);
  return (
    <div className="flex flex-wrap items-center gap-6">
      <svg viewBox="0 0 42 42" className="size-36 shrink-0" role="img" aria-label={fill(t(locale, "profile.acceptance"), { rate })}>
        <circle cx="21" cy="21" r="15.915" fill="none" stroke="var(--rw-chip)" strokeWidth="6" />
        {slices.map((slice) => {
          const part = (slice.value / total) * 100;
          const circle = (
            <circle
              key={slice.label}
              cx="21"
              cy="21"
              r="15.915"
              fill="none"
              stroke={slice.color}
              strokeWidth="6"
              strokeDasharray={`${part} ${100 - part}`}
              strokeDashoffset={offset}
            />
          );
          offset -= part;
          return circle;
        })}
        <text x="21" y="22.5" textAnchor="middle" className="fill-[var(--rw-text)] text-[7px] font-bold">
          {rate}%
        </text>
      </svg>
      <ul className="min-w-0 flex-1 space-y-1.5 text-theme-sm">
        {slices.map((slice) => (
          <li key={slice.label} className="flex items-center gap-2">
            <span aria-hidden="true" className="size-2.5 shrink-0 rounded-full" style={{ background: slice.color }} />
            <span className="min-w-0 flex-1 truncate rw-strong">{slice.label}</span>
            <span className="tabular-nums rw-faint">
              {slice.value} · {Math.round((slice.value / total) * 100)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Yechilgan/jami, daraja kesimi va verdiktlar ulushi. */
export function SolvedOverview({ stats, locale }: { stats: UserStats; locale: Locale }) {
  const share = stats.total ? Math.round((stats.solved / stats.total) * 100) : 0;
  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,22rem)]">
      <Card title={t(locale, "profile.solvedTitle")} bodyClassName="space-y-4">
        <SectionHint>{t(locale, "profile.solvedHint")}</SectionHint>
        <div>
          <p className="text-title-sm font-bold tabular-nums rw-strong">
            {stats.solved}
            <span className="text-theme-xl font-medium rw-faint"> / {stats.total}</span>
          </p>
          <div className="mt-2 h-2 overflow-hidden rounded-full rw-chip" role="progressbar" aria-valuenow={share} aria-valuemin={0} aria-valuemax={100} aria-label={t(locale, "profile.solvedTitle")}>
            <div className="h-full rounded-full" style={{ width: `${share}%`, background: "var(--rw-accent)" }} />
          </div>
        </div>
        <ul className="space-y-2">
          {stats.levels.map((level) => (
            <li key={level.code}>
              <div className="flex items-baseline justify-between gap-2 text-theme-sm">
                <span className={`level-${level.code} font-medium`}>{t(locale, `level.${level.code}`)}</span>
                <span className="tabular-nums rw-faint">
                  {level.solved} / {level.total}
                </span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip">
                <div
                  className={`level-${level.code} h-full rounded-full`}
                  style={{
                    width: `${level.total ? Math.round((level.solved / level.total) * 100) : 0}%`,
                    backgroundColor: "currentColor",
                  }}
                />
              </div>
            </li>
          ))}
        </ul>
      </Card>
      <Card title={t(locale, "profile.verdictsTitle")} bodyClassName="space-y-4">
        <SectionHint>{t(locale, "profile.verdictsHint")}</SectionHint>
        <VerdictDonut stats={stats} locale={locale} />
      </Card>
    </div>
  );
}
