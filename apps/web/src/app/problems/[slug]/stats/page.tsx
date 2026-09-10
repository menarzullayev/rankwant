import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";

import { ProblemTabs } from "@/components/ProblemTabs";
import { VerdictBadge } from "@/components/VerdictBadge";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { api, ApiError, type ProblemStats } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return { title: `Statistika · ${slug}` };
}

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

export default async function ProblemStatsPage({ params }: Props) {
  const locale = await getLocale();
  const { slug } = await params;

  let problem;
  let stats: ProblemStats;
  try {
    [problem, stats] = await Promise.all([
      api.problem(slug),
      api.problemStats(slug),
    ]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

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

      <ProblemTabs slug={slug} current="stats" />

      {stats.total === 0 ? (
        <Card>
          <p className="text-theme-sm rw-faint">
            Hali urinish yo&apos;q — statistika bo&apos;sh.
          </p>
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card title="Verdiktlar" bodyClassName="space-y-3">
            {stats.verdicts.map((row) => (
              <Share
                key={row.verdict}
                label={<VerdictBadge verdict={row.verdict} locale={locale} />}
                count={row.count}
                total={stats.total}
              />
            ))}
          </Card>

          <Card title="Tillar" bodyClassName="space-y-3">
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
              title="Eng tez yechimlar"
              className="lg:col-span-2"
              bodyClassName="p-0"
            >
              {/* Tilma-til: Python'ni C++ bilan bir jadvalda taqqoslash
                  yechim emas, tilni o'lchagan bo'lardi. */}
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
                href={`/problems/${slug}/solvers`}
                className="rw-accent-ink hover:underline"
              >
                Yechganlar
              </Link>{" "}
              bo&apos;limida.
            </p>
          </Card>
        </div>
      )}
    </div>
  );
}
