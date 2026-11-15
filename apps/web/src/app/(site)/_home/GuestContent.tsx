import type { Route } from "next";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { IntentLink } from "@/components/ui/IntentLink";
import { LEVEL_COLOR, LEVEL_LABEL, algorithmPath, isCategory, isLevel } from "@/features/algorithms";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { date, type Locale, t } from "@/i18n/messages";
import type { Article, Contest, Problem } from "@/lib/api";

/**
 * Public content for the guest home page (decision 2026-11-15): what a visitor who
 * arrives from a search engine can open without an account — the most opened problems,
 * the algorithms library and, when nothing is coming up, the last contests. Server
 * components only: the cached guest page carries the links as plain HTML, so a crawler
 * and a reader see the same thing.
 */

/** How many entries each block shows; the page links to the full list. */
export const POPULAR_PROBLEMS = 6;
export const LIBRARY_ARTICLES = 6;
export const RECENT_CONTESTS = 3;

/** Problems a visitor can actually try: the judge has tests for them. */
export function popularProblems(problems: Problem[]): Problem[] {
  return problems.filter((p) => p.has_tests).slice(0, POPULAR_PROBLEMS);
}

/** Algorithm articles with a place in the library (a category), newest listing order. */
export function libraryArticles(articles: Article[]): Article[] {
  return articles
    .filter((a) => a.kind === "algorithm" && isCategory(a.category))
    .slice(0, LIBRARY_ARTICLES);
}

/** Finished contests, the latest first. */
export function recentContests(contests: Contest[]): Contest[] {
  return contests
    .filter((c) => c.is_finished)
    .sort((a, b) => +new Date(b.end_at) - +new Date(a.end_at))
    .slice(0, RECENT_CONTESTS);
}

export function PopularProblems({ problems, locale }: { problems: Problem[]; locale: Locale }) {
  if (problems.length === 0) return null;
  return (
    <Card
      title={t(locale, "home.popularProblems")}
      action={
        <IntentLink href="/problems" className="text-theme-sm rw-accent-ink hover:underline">
          {t(locale, "home.all")}
        </IntentLink>
      }
      bodyClassName="p-0"
    >
      <ul className="divide-y rw-divide">
        {problems.map((p) => (
          <li key={p.slug}>
            <IntentLink
              href={`/problems/${p.slug}` as Route}
              className="flex items-center gap-3 px-5 py-3.5 transition rw-hover-bg"
            >
              {p.code !== null && (
                <span className="w-12 shrink-0 text-theme-xs rw-faint">
                  #{String(p.code).padStart(4, "0")}
                </span>
              )}
              <span className="min-w-0 flex-1 truncate font-medium rw-strong">
                {inReaderAlphabet(p.title, p.locale)}
              </span>
              <Badge>{p.difficulty}</Badge>
            </IntentLink>
          </li>
        ))}
      </ul>
    </Card>
  );
}

export function AlgorithmLibrary({ articles, locale }: { articles: Article[]; locale: Locale }) {
  if (articles.length === 0) return null;
  return (
    <Card
      title={t(locale, "nav.algorithms")}
      action={
        <IntentLink
          href={"/algorithms" as Route}
          className="text-theme-sm rw-accent-ink hover:underline"
        >
          {t(locale, "home.all")}
        </IntentLink>
      }
      bodyClassName="p-0"
    >
      <ul className="divide-y rw-divide">
        {articles.map((a) => (
          <li key={a.slug}>
            <IntentLink
              href={algorithmPath(a.category, a.slug) as Route}
              className="block px-5 py-3.5 transition rw-hover-bg"
            >
              <span className="flex items-center gap-2">
                <span className="min-w-0 flex-1 truncate font-medium rw-strong">
                  {inReaderAlphabet(a.title, a.locale)}
                </span>
                {isLevel(a.level) && (
                  <Badge color={LEVEL_COLOR[a.level]}>{t(locale, LEVEL_LABEL[a.level])}</Badge>
                )}
              </span>
              <span className="mt-1 line-clamp-2 block text-theme-sm rw-dim">
                {inReaderAlphabet(a.summary, a.locale)}
              </span>
            </IntentLink>
          </li>
        ))}
      </ul>
    </Card>
  );
}

export function RecentContests({ contests, locale }: { contests: Contest[]; locale: Locale }) {
  return (
    <Card
      title={t(locale, "home.recentContests")}
      action={
        <IntentLink href="/contests" className="text-theme-sm rw-accent-ink hover:underline">
          {t(locale, "home.all")}
        </IntentLink>
      }
      bodyClassName="p-0"
    >
      <ul className="divide-y rw-divide">
        {contests.map((c) => (
          <li key={c.slug}>
            <IntentLink
              href={`/contests/${c.slug}` as Route}
              className="flex items-center gap-3 px-5 py-4 transition rw-hover-bg"
            >
              <span className="min-w-0 flex-1">
                <span className="block truncate font-medium rw-strong">{c.title}</span>
                <span className="mt-0.5 block text-theme-xs rw-faint">
                  {date(c.end_at, locale)}
                </span>
              </span>
              <Badge>{t(locale, "contests.finished")}</Badge>
            </IntentLink>
          </li>
        ))}
      </ul>
    </Card>
  );
}
