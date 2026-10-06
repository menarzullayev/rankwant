import type { Metadata, Route } from "next";
import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { AttemptFilters, AttemptLiveProvider, AttemptTable } from "@/features/submissions";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { api, type Attempt, type Paginated } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { buildAttemptListHref } from "@/lib/problem-tabs";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "attempts.title") };
}

type Query = {
  cursor?: string | string[];
  verdict?: string | string[];
  language?: string | string[];
  mine?: string | string[];
  username?: string | string[];
  problem?: string | string[];
  ordering?: string | string[];
  size?: string | string[];
};

const one = (value: string | string[] | undefined) => (Array.isArray(value) ? value[0] : value);

/** The API's `max_page_size` is 100; anything else is dropped rather
 *  than sent, so a hand-typed `?size=99999` cannot turn into a 400. */
const pageSize = (raw: string | undefined) => (raw === "50" || raw === "100" ? raw : undefined);

/** The site-wide attempts feed.
 *
 *  The same table and filters as a problem's «Attempts» tab — one
 *  component, two places — with the problem as a column and a filter
 *  instead of a fixed context. Filters, order and page live in the URL
 *  and are applied by the server: the list is cursor-paged, so filtering
 *  in the browser would only ever search the rows already on screen.
 */
export default async function AttemptsPage({ searchParams }: { searchParams: Promise<Query> }) {
  const locale = await getLocale();
  const query = await searchParams;
  const cursor = one(query.cursor);
  const verdict = one(query.verdict);
  const language = one(query.language);
  const mine = one(query.mine) === "true";
  const username = one(query.username);
  const problem = one(query.problem);
  const ordering = one(query.ordering);
  const size = pageSize(one(query.size));

  const filters = new URLSearchParams();
  if (verdict) filters.set("verdict", verdict);
  if (language) filters.set("language", language);
  if (mine) filters.set("mine", "true");
  if (username) filters.set("username", username);
  if (problem) filters.set("problem", problem);
  if (ordering) filters.set("ordering", ordering);

  const request = new URLSearchParams(filters);
  if (size) request.set("page_size", size);
  if (cursor) request.set("cursor", cursor);
  const requestQuery = request.toString();

  const [page, languages] = await Promise.all([
    // "Mine" is a question about the session, and the plain SSR helper
    // sends no cookie: asked through it, the filter was silently ignored
    // and the page listed everybody.
    mine
      ? getWithSession<Paginated<Attempt>>(`/attempts/?${requestQuery}`)
      : api.attemptsQuery(requestQuery ? `?${requestQuery}` : ""),
    api.languages().catch(() => null),
  ]);

  const cursorOf = (link: string | null) => (link ? new URL(link).searchParams.get("cursor") : null);
  const nextCursor = cursorOf(page.next);
  const previousCursor = cursorOf(page.previous);

  const tableQuery = {
    verdict,
    language,
    mine: mine ? "true" : undefined,
    username,
    problem,
    ordering,
    size,
  };
  const pageHref = (target: string) =>
    `${buildAttemptListHref(undefined, tableQuery)}${
      Object.values(tableQuery).some(Boolean) ? "&" : "?"
    }cursor=${encodeURIComponent(target)}` as Route;

  const activeCount = [verdict, language, username, problem, mine ? "1" : ""].filter(
    Boolean,
  ).length;

  return (
    <AttemptLiveProvider>
      <div className="space-y-6">
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "attempts.title")}</h1>

        <AttemptFilters
          languages={(languages?.results ?? []).map(({ code, name }) => ({ code, name }))}
          verdict={verdict}
          language={language}
          mine={mine}
          username={username}
          problem={problem}
          size={size}
          ordering={ordering}
          activeCount={activeCount}
        />

        {page.results.length === 0 ? (
          <Card>
            <div className="px-5 py-12 text-center">
              <p className="text-theme-sm rw-strong">
                {activeCount > 0
                  ? t(locale, "attempts.emptyFilteredTitle")
                  : t(locale, "attempts.emptyTitle")}
              </p>
              {activeCount > 0 && (
                <p className="mt-1 text-theme-xs">
                  <Link href="/attempts" className="rw-accent-ink">
                    {t(locale, "attempts.clearFilters")}
                  </Link>
                </p>
              )}
            </div>
          </Card>
        ) : (
          <Card bodyClassName="p-0">
            <AttemptTable rows={page.results} ordering={ordering} query={tableQuery} />

            {(previousCursor || nextCursor) && (
              <nav
                aria-label={t(locale, "problem.pagination")}
                className="flex items-center justify-between gap-3 px-5 py-2"
              >
                {previousCursor ? (
                  <Link
                    href={pageHref(previousCursor)}
                    rel="prev"
                    className="inline-flex min-h-11 items-center text-theme-sm rw-dim-2 hover:underline"
                  >
                    {t(locale, "problem.previousPage")}
                  </Link>
                ) : (
                  <span />
                )}
                {nextCursor && (
                  <Link
                    href={pageHref(nextCursor)}
                    rel="next"
                    className="inline-flex min-h-11 items-center text-theme-sm rw-dim-2 hover:underline"
                  >
                    {t(locale, "problem.nextPage")}
                  </Link>
                )}
              </nav>
            )}
          </Card>
        )}
      </div>
    </AttemptLiveProvider>
  );
}
