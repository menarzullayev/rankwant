import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ProblemTabs } from "@/features/problems";
import { Card } from "@/components/ui/Card";
import { date, fill, t, type Locale } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { api, ApiError, type Solver } from "@/lib/api";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ ordering?: string }>;
};

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: Pick<Props, "params">): Promise<Metadata> {
  const { slug } = await params;
  const locale = await getLocale();
  return { title: `${t(locale, "problem.tab.solvers")} · ${slug}` };
}

/** Saralash — KEP'dagi «Solvers | Latest | Rating | Shortest Code».
 *  Har biri boshqa savolga javob beradi, shuning uchun bittasi yetmaydi. */
const ORDERINGS = [
  ["first", "problem.solvers.first"],
  ["fast", "problem.solvers.fast"],
  ["short", "problem.solvers.short"],
  ["tries", "problem.solvers.tries"],
] as const;

function Row({ solver, locale }: { solver: Solver; locale: Locale }) {
  return (
    <tr className="text-theme-sm">
      <td className="px-5 py-2.5">
        <Link
          href={`/users/${solver.username}`}
          className="font-medium rw-strong rw-link-hover"
        >
          {solver.username}
        </Link>
      </td>
      <td className="px-3 py-2.5 rw-dim">{solver.language}</td>
      <td className="px-3 py-2.5 text-right rw-dim tabular-nums">
        {solver.time_ms} ms
      </td>
      <td className="hidden px-3 py-2.5 text-right rw-faint tabular-nums sm:table-cell">
        {Math.round(solver.memory_kb / 1024)} MB
      </td>
      <td className="px-3 py-2.5 text-right rw-dim tabular-nums">
        {solver.code_length}
      </td>
      <td className="px-3 py-2.5 text-right rw-faint tabular-nums">
        {solver.attempts}
      </td>
      <td className="hidden px-5 py-2.5 text-right rw-faint md:table-cell">
        <time dateTime={solver.solved_at}>
          {date(solver.solved_at, locale)}
        </time>
      </td>
    </tr>
  );
}

export default async function SolversPage({ params, searchParams }: Props) {
  const locale = await getLocale();
  const { slug } = await params;
  const { ordering = "first" } = await searchParams;

  let problem;
  let solvers;
  try {
    [problem, solvers] = await Promise.all([
      api.problem(slug),
      api.problemSolvers(slug, ordering),
    ]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  const th = "px-3 py-2 text-right text-theme-xs font-medium rw-faint";

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

      <ProblemTabs slug={slug} current="solvers" />

      {solvers.count === 0 ? (
        <Card>
          <p className="text-theme-sm rw-faint">
            {t(locale, "problem.solvers.none")}
          </p>
        </Card>
      ) : (
        <Card
          title={fill(t(locale, "problem.solvers.count"), {
            count: solvers.count,
          })}
          action={
            <div className="flex flex-wrap gap-1">
              {ORDERINGS.map(([value, labelKey]) => (
                <Link
                  key={value}
                  href={`/problems/${slug}/solvers?ordering=${value}`}
                  aria-current={ordering === value ? "true" : undefined}
                  className={`rw-radius-sm px-2.5 py-1 text-theme-xs font-medium transition ${
                    ordering === value
                      ? "rw-accent-soft rw-accent-ink"
                      : "rw-dim rw-hover-bg"
                  }`}
                >
                  {t(locale, labelKey)}
                </Link>
              ))}
            </div>
          }
          bodyClassName="p-0"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b rw-divider">
                  <th className="px-5 py-2 text-left text-theme-xs font-medium rw-faint">
                    {t(locale, "standings.user")}
                  </th>
                  <th className="px-3 py-2 text-left text-theme-xs font-medium rw-faint">
                    {t(locale, "attempts.language")}
                  </th>
                  <th className={th}>{t(locale, "col.time")}</th>
                  <th className={`${th} hidden sm:table-cell`}>{t(locale, "col.memory")}</th>
                  <th className={th}>{t(locale, "problem.solvers.codeColumn")}</th>
                  <th className={th}>{t(locale, "col.attempt")}</th>
                  <th className={`${th} hidden px-5 md:table-cell`}>{t(locale, "profile.date")}</th>
                </tr>
              </thead>
              <tbody className="rw-divide divide-y">
                {solvers.results.map((solver) => (
                  <Row key={solver.username} solver={solver} locale={locale} />
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
