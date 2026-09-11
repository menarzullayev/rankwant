import Link from "next/link";

import { DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { t, type Locale } from "@/i18n/messages";
import { api, type UserPublic } from "@/lib/api";

const REASON_LABEL: Record<string, string> = {
  problem_solved: "masala yechildi",
  problem_rerated: "masala qayta baholandi",
  contest: "musobaqa",
  recalculation: "qayta hisoblash",
};

/** Reyting bo'limi — daraja kesimi, o'zgarishlar tarixi va yechilganlar. */
export async function RatingTab({
  user,
  locale,
}: {
  user: UserPublic;
  locale: Locale;
}) {
  const [history, solved] = await Promise.all([
    api.ratingHistory(user.username),
    api.solved(user.username),
  ]);
  const solvedLevels = user.solved_by_level.filter((level) => level.solved > 0);
  const peakLevel = Math.max(...solvedLevels.map((l) => l.solved), 1);

  return (
    <div className="space-y-6">
      {solvedLevels.length > 0 && (
        <Card title={t(locale, "profile.byLevel")} bodyClassName="space-y-2.5">
          {solvedLevels.map((level) => (
            <div key={level.code}>
              <div className="flex items-baseline justify-between gap-2 text-theme-sm">
                <span className={`level-${level.code} font-medium`}>{level.label}</span>
                <span className="rw-faint tabular-nums">{level.solved}</span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip">
                <div
                  className={`level-${level.code} h-full rounded-full`}
                  style={{
                    width: `${Math.round((level.solved / peakLevel) * 100)}%`,
                    backgroundColor: "currentColor",
                  }}
                />
              </div>
            </div>
          ))}
        </Card>
      )}

      {/* Principle #2 ning ko'rinadigan qismi: har o'zgarish sababi bilan */}
      <Card
        title={t(locale, "profile.history")}
        action={
          <Link href="/rating" className="text-theme-sm rw-accent-ink hover:underline">
            {t(locale, "nav.ratingInfo")}
          </Link>
        }
        bodyClassName="p-0"
      >
        <Table>
          <THead>
            <TH>{t(locale, "profile.ratingColumn")}</TH>
            <TH align="right">{t(locale, "profile.change")}</TH>
            <TH>{t(locale, "profile.reason")}</TH>
            <TH align="right">{t(locale, "profile.date")}</TH>
          </THead>
          <TBody>
            {history.results.map((row, i) => (
              <TR key={`${row.created_at}-${i}`}>
                <TD className="font-medium rw-strong">{row.rating_type}</TD>
                <TD align="right">
                  <span
                    className={
                      row.delta >= 0 ? "font-semibold rw-ok-ink" : "font-semibold rw-bad-ink"
                    }
                  >
                    {row.delta > 0 ? "+" : ""}
                    {row.delta}
                  </span>
                </TD>
                <TD className="rw-dim">
                  {REASON_LABEL[row.reason] ?? row.reason}
                  {row.rank !== null && ` · #${row.rank}`}
                  {row.ref_id && ` · ${row.ref_id}`}
                </TD>
                <TD align="right" className="rw-faint">
                  {new Date(row.created_at).toLocaleDateString(locale)}
                </TD>
              </TR>
            ))}
            {history.results.length === 0 && (
              <EmptyRow colSpan={4}>{t(locale, "empty")}</EmptyRow>
            )}
          </TBody>
        </Table>
      </Card>

      <Card title={t(locale, "profile.solved")}>
        <div className="flex flex-wrap gap-2">
          {solved.results.map((p) => (
            <Link
              key={p.slug}
              href={`/problems/${p.slug}`}
              className="flex items-center gap-2 rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm transition rw-hover-line"
              // Joriy va yechilgandagi qiyinlik farq qilsa — qayta baholangan
              title={
                p.difficulty !== p.difficulty_at_solve
                  ? `${p.difficulty_at_solve} → ${p.difficulty} (${t(locale, "profile.rerated")})`
                  : undefined
              }
            >
              <span className="rw-strong">{p.title}</span>
              <DifficultyBadge value={p.difficulty} />
              {p.difficulty !== p.difficulty_at_solve && (
                <span className="rw-warn-ink" aria-hidden="true">
                  *
                </span>
              )}
            </Link>
          ))}
          {solved.results.length === 0 && (
            <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
          )}
        </div>
      </Card>
    </div>
  );
}
