import type { Route } from "next";

import { Badge } from "@/components/ui/Badge";
import { IntentLink } from "@/components/ui/IntentLink";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { fill, type Locale, t } from "@/i18n/messages";
import type { ProblemDetail } from "@/lib/api";

import { HeroActions } from "./HeroActions";
import { heroSample, plainStatement } from "./hero-model";

/**
 * The first block of the guest home page (decision 2026-11-15; the discussion and its
 * nine decisions are in `docs/decisions/2026-11-15-guest-hero.md`).
 *
 * Two columns from `lg`, one below it: the promise, the two buttons and four numbers on
 * the left; a REAL public problem on the right — its statement, a sample, its limits and
 * a way in. The card has no code editor: a guest does not see one (ADR-0054).
 *
 * The numbers describe what the platform can do and are read from the database; the
 * number of users is not shown (it is mostly imported accounts, and the people who
 * really use the site are still few).
 */

export type HeroNumbers = {
  languages: number;
  problems: number;
  articles: number;
  interfaces: number;
};

export function GuestHero({
  locale,
  numbers,
  problem,
}: {
  locale: Locale;
  numbers: HeroNumbers;
  problem: ProblemDetail | null;
}) {
  const items: { value: number; label: string }[] = [
    { value: numbers.languages, label: t(locale, "home.statLanguages") },
    { value: numbers.problems, label: t(locale, "home.statProblems") },
    { value: numbers.articles, label: t(locale, "home.statArticles") },
    { value: numbers.interfaces, label: t(locale, "home.statInterface") },
  ];

  return (
    <section className="rw-radius border rw-line rw-surface px-6 py-8 rw-shadow lg:py-10">
      <div className="grid gap-8 lg:grid-cols-2 lg:items-center">
        <div>
          <p className="text-theme-sm font-medium rw-accent-ink">
            RankWant · {t(locale, "home.heroTagline")}
          </p>
          <h1 className="mt-3 text-title-sm font-bold text-balance rw-strong sm:text-title-md">
            {t(locale, "home.heroHeadline")}
          </h1>
          <p className="mt-4 max-w-xl text-theme-sm rw-dim">{t(locale, "home.heroLead")}</p>
          <HeroActions
            start={t(locale, "home.start")}
            browse={t(locale, "home.browseProblems")}
          />
          <p className="mt-4 text-theme-xs rw-faint">{t(locale, "home.guestHint")}</p>

          <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-4 sm:grid-cols-4">
            {items.map((item) => (
              <div key={item.label} className="flex flex-col-reverse">
                <dt className="text-theme-xs rw-faint">{item.label}</dt>
                <dd className="text-theme-xl font-semibold rw-strong">{item.value}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-1 text-theme-xs">
            <IntentLink
              href="/rating"
              className="inline-flex min-h-11 items-center rw-accent-ink hover:underline"
            >
              {t(locale, "nav.ratingInfo")}
            </IntentLink>
          </p>
        </div>

        {problem && <ProblemCard locale={locale} problem={problem} />}
      </div>
    </section>
  );
}

function ProblemCard({ locale, problem }: { locale: Locale; problem: ProblemDetail }) {
  const sample = heroSample(problem.samples);
  const href = `/problems/${problem.slug}` as Route;
  const statement = plainStatement(inReaderAlphabet(problem.statement, problem.statement_locale));

  return (
    <aside
      aria-label={t(locale, "home.heroProblemLabel")}
      className="min-w-0 rw-radius border rw-line p-5"
    >
      <p className="text-theme-xs font-medium rw-faint">{t(locale, "home.heroProblemLabel")}</p>
      <div className="mt-2 flex items-start justify-between gap-3">
        <h2 className="min-w-0 text-theme-xl font-semibold rw-strong">
          <IntentLink href={href} className="inline-block py-2.5 hover:underline">
            {problem.code !== null && (
              <span className="rw-faint">#{String(problem.code).padStart(4, "0")} · </span>
            )}
            {inReaderAlphabet(problem.title, problem.locale)}
          </IntentLink>
        </h2>
        <Badge>{problem.difficulty}</Badge>
      </div>

      {statement && <p className="mt-3 text-theme-sm rw-dim">{statement}</p>}

      <div className="mt-3 flex flex-wrap gap-2">
        <Badge>
          {fill(t(locale, "contest.print.limits"), {
            time: problem.time_limit_ms,
            memory: Math.round(problem.memory_limit_kb / 1024),
          })}
        </Badge>
      </div>

      {sample && (
        <div className="mt-4 grid grid-cols-2 gap-3">
          <div className="min-w-0">
            <p className="text-theme-xs rw-faint">{t(locale, "problem.sampleInput")}</p>
            <pre className="mt-1 rw-scroll rw-radius-sm rw-field-bg p-2 font-mono text-theme-xs rw-strong">
              {sample.input}
            </pre>
          </div>
          <div className="min-w-0">
            <p className="text-theme-xs rw-faint">{t(locale, "problem.sampleOutput")}</p>
            <pre className="mt-1 rw-scroll rw-radius-sm rw-field-bg p-2 font-mono text-theme-xs rw-strong">
              {sample.expected}
            </pre>
          </div>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between gap-3 border-t rw-divider pt-3">
        <span className="text-theme-xs rw-faint">{t(locale, "gate.solve.title")}</span>
        <IntentLink
          href={href}
          className="inline-flex min-h-11 shrink-0 items-center text-theme-sm font-medium rw-accent-ink hover:underline"
        >
          {t(locale, "home.openProblem")}
        </IntentLink>
      </div>
    </aside>
  );
}
