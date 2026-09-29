import Link from "next/link";

import { Attachments } from "@/features/submissions";
import { Markdown } from "@/components/ui/Markdown";
import { ReportProblem, SimilarProblems } from "@/features/problems";
import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { CopyButton } from "@/components/kit/CopyControl";
import { ProblemActions } from "@/features/problems";
import { SampleTests } from "@/features/problems";
import { StatementSize } from "@/features/problems";
import { fill, t, type Locale } from "@/i18n/messages";
import type { ProblemDetail } from "@/lib/api";

/** Tavsif tab paneli — mavjud masala matni va metadata.
 *
 *  Eski `/problems/[slug]` sahifasidan ko'chirilgan, o'zgarishsiz:
 *  tahrir faqat `Editorial` ni ajratish (endi alohida tabda).
 *  Soxta/mavhum ma'lumot yo'q — hammasi `ProblemDetail` dan.
 */
export function ProblemDescription({
  problem,
  slug,
  contest,
  locale,
}: {
  problem: ProblemDetail;
  slug: string;
  contest?: string;
  locale: Locale;
}) {
  return (
    <article className="min-w-0 space-y-6">
      <header>
        <div className="rw-kit-hover flex flex-wrap items-baseline gap-3">
          {problem.code !== null && (
            <span className="font-mono text-theme-sm rw-faint tabular-nums">
              #{String(problem.code).padStart(4, "0")}
            </span>
          )}
          <h1 className="text-title-sm font-bold rw-strong">{problem.title}</h1>
          <CopyButton text={slug} tone="hover" />
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <DifficultyBadge value={problem.difficulty} />
          <span className={`level-${problem.level} text-theme-sm font-medium`}>
            {problem.level_label}
          </span>
          <Badge>
            {t(locale, "problems.limits")}: {problem.time_limit_ms} ms,{" "}
            {Math.round(problem.memory_limit_kb / 1024)} MB
          </Badge>
          {problem.partial_scoring && (
            <Badge color="info">{t(locale, "problem.partialScoring")}</Badge>
          )}
          {!problem.has_tests && (
            <Badge color="warning">{t(locale, "problem.testsPreparing")}</Badge>
          )}
          {problem.topics.map((topic) => (
            <Badge key={topic} color="info">
              {topic}
            </Badge>
          ))}
        </div>

        <p className="mt-3 text-theme-sm rw-dim">
          {problem.author && (
            <>
              {t(locale, "problem.author")}:{" "}
              {problem.author.has_profile ? (
                <Link
                  href={`/users/${problem.author.username}`}
                  className="rw-link-hover"
                >
                  {problem.author.display_name}
                </Link>
              ) : (
                problem.author.display_name
              )}{" "}
              ·{" "}
            </>
          )}
          {fill(t(locale, "problem.solvedAttempts"), {
            solved: problem.solved_count,
            attempts: problem.attempt_count,
          })}
          {problem.attempt_count > 0 &&
            ` · ${fill(t(locale, "problem.successRate"), {
              percent: Math.round(
                (problem.solved_count / problem.attempt_count) * 100,
              ),
            })}`}
        </p>

        <div className="mt-2">
          <ProblemActions problem={problem} />
        </div>
      </header>

      {contest && (
        <p className="rw-radius-sm rw-accent-soft px-4 py-2.5 text-theme-sm rw-accent-ink">
          {fill(t(locale, "problem.countedInContest"), { contest })}{" "}
          <Link href={`/contests/${contest}`} className="underline">
            {t(locale, "problem.backToContest")}
          </Link>
        </p>
      )}

      <Card>
        <StatementSize>
          <div className="space-y-5">
            {problem.image && (
              /* eslint-disable-next-line @next/next/no-img-element --
                 rasm import qilingan arxivning tashqi domenida; uni
                 `next/image` ga berish har bir manba uchun alohida
                 `remotePatterns` yozishni talab qilardi. */
              <img
                src={problem.image}
                alt=""
                className="w-full rw-radius-sm"
              />
            )}
            <Markdown>{problem.statement}</Markdown>

            {problem.input_format && (
              <section>
                <h2 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                  {t(locale, "problem.inputFormat")}
                </h2>
                <Markdown>{problem.input_format}</Markdown>
              </section>
            )}

            {problem.output_format && (
              <section>
                <h2 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                  {t(locale, "problem.outputFormat")}
                </h2>
                <Markdown>{problem.output_format}</Markdown>
              </section>
            )}
          </div>
        </StatementSize>
      </Card>

      <SampleTests samples={problem.samples} />

      {problem.note && (
        <Card title={t(locale, "problem.comments")}>
          <Markdown>{problem.note}</Markdown>
        </Card>
      )}

      <Attachments items={problem.attachments} locale={locale} />

      <SimilarProblems items={problem.similar} locale={locale} />

      <ReportProblem slug={slug} />

      {problem.source && (
        <p className="text-theme-sm rw-faint">
          {t(locale, "problem.source")}:{" "}
          {problem.source_url ? (
            <a
              href={problem.source_url}
              rel="noopener noreferrer"
              className="underline"
            >
              {problem.source}
            </a>
          ) : (
            problem.source
          )}
          {problem.source_rating !== null &&
            ` · ${fill(t(locale, "problem.sourceRating"), {
              rating: problem.source_rating,
            })}`}
        </p>
      )}
    </article>
  );
}
