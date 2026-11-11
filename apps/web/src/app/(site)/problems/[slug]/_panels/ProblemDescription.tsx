import Link from "next/link";

import { Attachments } from "@/features/submissions";
import { Markdown } from "@/components/ui/Markdown";
import {
  Editorial,
  ProblemActions,
  ProblemMetaAccordion,
  ProblemSolveTimer,
  ProblemStatementCard,
  ReportProblem,
  SampleTests,
  StatementTextSizeControls,
  VerdictPresentationLayer,
} from "@/features/problems";
import { Badge, DifficultyBadge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { CopyButton } from "@/components/kit/CopyControl";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { fill, LOCALE_NAMES, t, type Locale } from "@/i18n/messages";
import type { ProblemDetail } from "@/lib/api";
import { stripDuplicateStatementHeading } from "@/lib/statement-body";
import { formatTolerance } from "@/lib/tolerance";

/** Tavsif tab paneli — mavjud masala matni va metadata.
 *
 *  Eski `/problems/[slug]` sahifasidan ko'chirilgan. P0 tahlil endi
 *  tavsif tabida namunalar ostida ham (`Editorial`), alohida tab saqlanadi.
 */
/** Solvers per attempt, in percent. A handful of solvers against a
 *  thousand attempts rounds to `0`, which reads as "nobody solved it"
 *  right next to the solved count — so a non-zero share never shows as 0. */
function successPercent(solved: number, attempts: number): string {
  const percent = Math.round((solved / attempts) * 100);
  return solved > 0 && percent === 0 ? "<1" : String(percent);
}

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
  const statementBody = stripDuplicateStatementHeading(
    problem.statement,
    problem.title,
  );

  return (
    <article className="min-w-0 space-y-6">
      <ProblemSolveTimer
        slug={slug}
        contestEndsAt={problem.contest?.is_running ? problem.contest.end_at : undefined}
      />
      <VerdictPresentationLayer placement="column" />
      <header>
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-2">
          {problem.code !== null && (
            <span className="font-mono text-theme-sm rw-faint tabular-nums">
              #{String(problem.code).padStart(4, "0")}
            </span>
          )}
          <h1 className="text-title-sm font-bold rw-strong">
            {inReaderAlphabet(problem.title, problem.locale)}
          </h1>
          {!problem.is_official && (
            // ADR-0060 § 2.3: it has no number, and the solver should know
            // what its solve counts for.
            <span
              className="rw-radius-full border rw-line px-2.5 py-1 text-theme-xs font-semibold rw-dim"
              title={t(locale, "problems.tier.hint")}
            >
              {t(locale, "problem.unofficial")}
            </span>
          )}
          <span className="grow" />
          <span className="rw-radius-full rw-warn-soft px-2.5 py-1 text-theme-xs font-semibold rw-warn-ink tabular-nums">
            {problem.time_limit_ms} ms · {Math.round(problem.memory_limit_kb / 1024)}{" "}
            MB
          </span>
          {problem.checker_type === "real" && (
            // ADR-0060: the solver needs to know the answer is not compared
            // character by character, and how close is close enough.
            <span
              className="rw-radius-full rw-warn-soft px-2.5 py-1 text-theme-xs font-semibold rw-warn-ink tabular-nums"
              title={fill(t(locale, "problem.realToleranceHint"), {
                eps: formatTolerance(problem.real_tolerance),
              })}
            >
              {fill(t(locale, "problem.realTolerance"), {
                eps: formatTolerance(problem.real_tolerance),
              })}
            </span>
          )}
          <StatementTextSizeControls />
          <CopyButton text={slug} size="sm" />
        </div>
        {problem.locale !== locale && (
          // ADR-0058: no translation in the reader's language yet.
          <p className="mt-2 text-theme-xs rw-faint">
            {fill(t(locale, "problem.notTranslated"), {
              locale: LOCALE_NAMES[locale] ?? locale,
              shown: LOCALE_NAMES[problem.locale as Locale] ?? problem.locale,
            })}
          </p>
        )}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <DifficultyBadge value={problem.difficulty} />
          <span className={`level-${problem.level} text-theme-sm font-medium`}>
            {t(locale, `level.${problem.level}`)}
          </span>
          {problem.topics.map((topic) => (
            <Badge key={topic} color="neutral">
              {topic}
            </Badge>
          ))}
          {problem.partial_scoring && (
            <Badge color="info">{t(locale, "problem.partialScoring")}</Badge>
          )}
          {!problem.has_tests && (
            <Badge color="warning">{t(locale, "problem.testsPreparing")}</Badge>
          )}
          {/* Audit Q-05: only samples — a printed sample is accepted, so
              the solve earns no Skills or Qvant. Say it before the attempt. */}
          {problem.has_tests && !problem.has_hidden_tests && (
            <span title={t(locale, "problem.samplesOnlyHint")}>
              <Badge color="warning">{t(locale, "problem.samplesOnly")}</Badge>
            </span>
          )}
          <span className="ml-auto text-theme-xs rw-dim tabular-nums">
            {fill(t(locale, "problem.solvedAttempts"), {
              solved: problem.solved_count,
              attempts: problem.attempt_count,
            })}
            {problem.attempt_count > 0 &&
              ` · ${fill(t(locale, "problem.successRate"), {
                percent: successPercent(problem.solved_count, problem.attempt_count),
              })}`}
          </span>
        </div>

        {problem.author && (
          <p className="mt-2 text-theme-sm rw-dim">
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
            )}
          </p>
        )}

        <div>
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
        <ProblemStatementCard>
          <div id="problem-statement" className="space-y-5">
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
            <Markdown lang={problem.locale}>{statementBody}</Markdown>

            {problem.input_format && (
              <section id="problem-input-format">
                <h2 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                  {t(locale, "problem.inputFormat")}
                </h2>
                <Markdown lang={problem.locale}>{problem.input_format}</Markdown>
              </section>
            )}

            {problem.output_format && (
              <section id="problem-output-format">
                <h2 className="mb-1.5 text-theme-lg font-semibold rw-strong">
                  {t(locale, "problem.outputFormat")}
                </h2>
                <Markdown lang={problem.locale}>{problem.output_format}</Markdown>
              </section>
            )}
          </div>
        </ProblemStatementCard>
      </Card>

      <div id="problem-samples">
        <SampleTests samples={problem.samples} />
      </div>
      <p className="text-theme-xs rw-faint">{t(locale, "problem.sampleRunHint")}</p>

      {problem.editorial_state.available && (
        <div id="problem-editorial">
          <Editorial
            slug={slug}
            text={problem.editorial}
            state={problem.editorial_state}
            lang={problem.locale}
          />
        </div>
      )}

      <ProblemMetaAccordion
        topics={problem.topics}
        similar={problem.similar}
        locale={locale}
      />

      {problem.note && (
        <div id="problem-notes">
          <Card title={t(locale, "problem.comments")}>
            <Markdown lang={problem.locale}>{problem.note}</Markdown>
          </Card>
        </div>
      )}

      <Attachments items={problem.attachments} locale={locale} />

      <ReportProblem slug={slug} />

      <VerdictPresentationLayer placement="toast" />
      <VerdictPresentationLayer placement="modal" />

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
