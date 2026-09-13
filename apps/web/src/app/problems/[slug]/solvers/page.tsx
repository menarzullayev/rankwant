import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ProblemTabs } from "@/components/ProblemTabs";
import { Card } from "@/components/ui/Card";
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
  return { title: `Yechganlar · ${slug}` };
}

/** Saralash — KEP'dagi «Solvers | Latest | Rating | Shortest Code».
 *  Har biri boshqa savolga javob beradi, shuning uchun bittasi yetmaydi. */
const ORDERINGS = [
  ["first", "Birinchi yechganlar"],
  ["fast", "Eng tez"],
  ["short", "Eng qisqa kod"],
  ["tries", "Kam urinish"],
] as const;

function Row({ solver }: { solver: Solver }) {
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
          {new Date(solver.solved_at).toLocaleDateString("uz")}
        </time>
      </td>
    </tr>
  );
}

export default async function SolversPage({ params, searchParams }: Props) {
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
            Bu masalani hali hech kim yechmagan — birinchi bo&apos;ling.
          </p>
        </Card>
      ) : (
        <Card
          title={`${solvers.count} kishi yechdi`}
          action={
            <div className="flex flex-wrap gap-1">
              {ORDERINGS.map(([value, label]) => (
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
                  {label}
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
                    Foydalanuvchi
                  </th>
                  <th className="px-3 py-2 text-left text-theme-xs font-medium rw-faint">
                    Til
                  </th>
                  <th className={th}>Vaqt</th>
                  <th className={`${th} hidden sm:table-cell`}>Xotira</th>
                  <th className={th}>Kod, belgi</th>
                  <th className={th}>Urinish</th>
                  <th className={`${th} hidden px-5 md:table-cell`}>Sana</th>
                </tr>
              </thead>
              <tbody className="rw-divide divide-y">
                {solvers.results.map((solver) => (
                  <Row key={solver.username} solver={solver} />
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
