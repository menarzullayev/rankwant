import Link from "next/link";
import type { Route } from "next";

import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Verdict } from "@/components/ui/Verdict";
import { t, type Locale } from "@/i18n/messages";
import { api, type ProblemDetail } from "@/lib/api";

/** Ulush chizig'i — diagramma kutubxonasi shu bitta blok uchun ortiqcha. */
function Share({
  label,
  count,
  total,
  hint,
}: {
  label: React.ReactNode;
  count: number;
  total: number;
  hint?: string;
}) {
  const percent = total ? Math.round((count / total) * 100) : 0;

  return (
    <div>
      <div className="flex items-baseline justify-between gap-3 text-theme-sm">
        <span className="flex items-center gap-2">{label}</span>
        <span className="rw-faint tabular-nums">
          {count} · {percent}%{hint ? ` · ${hint}` : ""}
        </span>
      </div>
      <div className="mt-1 h-1.5 overflow-hidden rounded-full rw-chip">
        <div
          className="h-full rounded-full rw-accent-bg"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

/** Statistika tab paneli — mavjud API, soxta raqam yo'q.
 *
 *  Eski `/stats` sahifasidan ko'chirilgan. Urinish bo'lmasa bo'sh holat;
 *  yechganlar ro'yxati havolasi yangi manzilga (`?tab=solvers`).
 *  Yetishmaydigan qatlam yo'q: `api.problemStats` backend'da bor.
 */
export async function ProblemStatsPanel({
  problem,
  slug,
  locale,
}: {
  problem: ProblemDetail;
  slug: string;
  locale: Locale;
}) {
  const stats = await api.problemStats(slug);

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {problem.code !== null && (
          <span className="mr-2 font-mono text-theme-sm rw-faint tabular-nums">
            #{String(problem.code).padStart(4, "0")}
          </span>
        )}
        {problem.title}
      </h1>

      {stats.total === 0 ? (
        <Card>
          <EmptyState
            variant="card"
            title={t(locale, "problem.stats.empty")}
            hint={t(locale, "common.emptyHint")}
          />
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card title={t(locale, "profile.verdictsTitle")} bodyClassName="space-y-3">
            {stats.verdicts.map((row) => (
              <Share
                key={row.verdict}
                label={<Verdict verdict={row.verdict} />}
                count={row.count}
                total={stats.total}
              />
            ))}
          </Card>

          <Card title={t(locale, "problem.stats.languages")} bodyClassName="space-y-3">
            {stats.languages.map((row) => (
              <Share
                key={row.language}
                label={
                  <span className="font-medium rw-strong">{row.language}</span>
                }
                count={row.count}
                total={stats.total}
                hint={`${row.solved} AC`}
              />
            ))}
          </Card>

          {stats.fastest.length > 0 && (
            <Card
              title={t(locale, "problem.stats.fastest")}
              className="lg:col-span-2"
              bodyClassName="p-0"
            >
              <ul className="rw-divide divide-y">
                {stats.fastest.map((row) => (
                  <li
                    key={row.language}
                    className="flex flex-wrap items-center gap-3 px-5 py-2.5 text-theme-sm"
                  >
                    <span className="font-medium rw-strong">
                      {row.language}
                    </span>
                    <Link
                      href={`/users/${row.username}`}
                      className="rw-dim rw-link-hover"
                    >
                      {row.username}
                    </Link>
                    <span className="ml-auto font-medium rw-accent-ink tabular-nums">
                      {row.time_ms} ms
                    </span>
                    <span className="rw-faint tabular-nums">
                      {Math.round(row.memory_kb / 1024)} MB
                    </span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          <Card className="lg:col-span-2">
            <p className="text-theme-sm rw-dim">
              Kim yechgani, nechanchi urinishda va qanday kod bilan —{" "}
              <Link
                href={`/problems/${slug}?tab=solvers` as Route}
                className="rw-accent-ink hover:underline"
              >
                {t(locale, "problem.tab.solvers")}
              </Link>{" "}
              bo&apos;limida.
            </p>
          </Card>
        </div>
      )}
    </div>
  );
}
