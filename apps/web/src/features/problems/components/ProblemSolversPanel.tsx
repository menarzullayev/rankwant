import Link from "next/link";
import type { Route } from "next";

import { Card } from "@/components/ui/Card";
import { date, fill, t, type Locale } from "@/i18n/messages";
import { api, type ProblemDetail, type Solver } from "@/lib/api";
import { buildSolversHref } from "@/lib/problem-tabs";

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

/** Yechganlar tab paneli — mavjud API, maxfiylik qoidasi o'zgarmaydi.
 *
 *  Eski `/solvers` sahifasidan ko'chirilgan, farqi faqat manzil:
 *  `?ordering=` endi `?tab=solvers&ordering=` ichida. Ro'yxat ochiq;
 *  kodning o'zi ko'rinmaydi (faqat uzunligi) — manba himoyasi
 *  urinishlar API'da (`AttemptDetail.source_code` faqat egasiga).
 */
export async function ProblemSolversPanel({
  problem,
  slug,
  ordering,
  locale,
}: {
  problem: ProblemDetail;
  slug: string;
  ordering: string;
  locale: Locale;
}) {
  const solvers = await api.problemSolvers(slug, ordering);
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
                  href={buildSolversHref(slug, value) as Route}
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
