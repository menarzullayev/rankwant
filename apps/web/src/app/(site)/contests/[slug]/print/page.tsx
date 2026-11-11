import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Markdown } from "@/components/ui/Markdown";
import { PrintButton } from "@/features/contests";
import type { ProblemDetail } from "@/features/problems";
import { fill, t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { api, ApiError } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { stripDuplicateStatementHeading } from "@/lib/statement-body";

type Props = { params: Promise<{ slug: string }> };

export const dynamic = "force-dynamic";

/** The statements of a contest as one document to print or save as PDF
 *  (decision 2026-11-10 ②: an offline olympiad, a printed set).
 *
 *  The same visibility as everywhere else (ADR-0055): before the start the
 *  contest answers with no problems and this page says when they open. A
 *  copy of the problem pages, so search engines are kept off it. */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const locale = await getLocale();
  try {
    const contest = await api.contest(slug);
    return {
      title: fill(t(locale, "contest.print.title"), { contest: contest.title }),
      robots: { index: false, follow: false },
    };
  } catch {
    return { title: t(locale, "contest.notFound"), robots: { index: false } };
  }
}

const MB = 1024;

export default async function ContestPrintPage({ params }: Props) {
  const { slug } = await params;
  const locale = await getLocale();

  let contest;
  try {
    contest = await api.contest(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  const problems = await Promise.all(
    contest.problems.map(async (entry) => ({
      entry,
      problem: await getWithSession<ProblemDetail>(
        `/problems/${entry.slug}/?lang=${locale}`,
      ).catch(() => null),
    })),
  );
  const ready = problems.filter(
    (item): item is { entry: (typeof problems)[number]["entry"]; problem: ProblemDetail } =>
      item.problem !== null,
  );

  return (
    <div className="rw-print mx-auto max-w-[52rem] px-4 py-6 sm:px-8" data-contest-print="">
      <div className="mb-6 flex flex-wrap items-center gap-3 print:hidden" data-print-toolbar="">
        <Link href={`/contests/${slug}`} className="text-theme-sm rw-accent-ink hover:underline">
          {t(locale, "contest.print.back")}
        </Link>
        <span className="grow" />
        {ready.length > 0 && <PrintButton label={t(locale, "contest.print.button")} />}
      </div>
      {ready.length > 0 && (
        <p className="mb-6 text-theme-sm rw-dim print:hidden">{t(locale, "contest.print.hint")}</p>
      )}

      <header className="mb-8 border-b rw-divider pb-4">
        <h1 className="text-title-sm font-bold rw-strong">{contest.title}</h1>
        <p className="mt-1 text-theme-sm rw-dim">
          {fill(t(locale, "contest.print.count"), { count: ready.length })}
        </p>
      </header>

      {ready.length === 0 && (
        <p className="rw-radius border rw-line rw-surface p-5 text-theme-sm rw-dim" data-problems-hidden="">
          {contest.problem_count > 0
            ? fill(t(locale, "contest.problemsAtStart"), { count: contest.problem_count })
            : t(locale, "common.empty")}
        </p>
      )}

      {ready.map(({ entry, problem }, index) => (
        <section
          key={entry.slug}
          className={`rw-print-problem space-y-4 ${index > 0 ? "mt-12 break-before-page" : ""}`}
          data-print-problem={entry.index_letter}
        >
          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
            <h2 className="text-title-sm font-bold rw-strong">
              {entry.index_letter}. {problem.title}
            </h2>
            <span className="text-theme-sm tabular-nums rw-dim">
              {fill(t(locale, "contest.print.limits"), {
                time: problem.time_limit_ms,
                memory: Math.round(problem.memory_limit_kb / MB),
              })}
            </span>
          </div>
          {problem.image && (
            /* eslint-disable-next-line @next/next/no-img-element --
               the statement's own picture, from wherever the archive keeps
               it; the problem page draws it the same way. */
            <img src={problem.image} alt="" className="w-full rw-radius-sm" />
          )}
          <Markdown lang={problem.locale}>
            {stripDuplicateStatementHeading(problem.statement, problem.title)}
          </Markdown>
          {problem.input_format && (
            <div>
              <h3 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                {t(locale, "problem.inputFormat")}
              </h3>
              <Markdown lang={problem.locale}>{problem.input_format}</Markdown>
            </div>
          )}
          {problem.output_format && (
            <div>
              <h3 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                {t(locale, "problem.outputFormat")}
              </h3>
              <Markdown lang={problem.locale}>{problem.output_format}</Markdown>
            </div>
          )}
          {problem.samples.length > 0 && (
            <div>
              <h3 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                {t(locale, "problem.samples")}
              </h3>
              <table className="w-full table-fixed border-collapse text-theme-sm">
                <thead>
                  <tr>
                    <th className="border rw-line px-3 py-1.5 text-left font-semibold">
                      {t(locale, "problem.sampleInput")}
                    </th>
                    <th className="border rw-line px-3 py-1.5 text-left font-semibold">
                      {t(locale, "problem.sampleOutput")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {problem.samples.map((sample) => (
                    <tr key={sample.order} className="break-inside-avoid align-top">
                      <td className="border rw-line px-3 py-2">
                        <pre className="whitespace-pre-wrap break-all font-mono">{sample.input}</pre>
                      </td>
                      <td className="border rw-line px-3 py-2">
                        <pre className="whitespace-pre-wrap break-all font-mono">{sample.expected}</pre>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {problem.note && (
            <div>
              <h3 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                {t(locale, "problem.comments")}
              </h3>
              <Markdown lang={problem.locale}>{problem.note}</Markdown>
            </div>
          )}
        </section>
      ))}
    </div>
  );
}
