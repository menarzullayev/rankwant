import Link from "next/link";
import type { Route } from "next";

import { Card } from "@/components/ui/Card";
import { fill, t, type Locale } from "@/i18n/messages";
import {
  AttemptFilters,
  AttemptLiveProvider,
  AttemptTable,
} from "@/features/submissions";
import { api, type ProblemDetail } from "@/lib/api";
import { buildAttemptsHref } from "@/lib/problem-tabs";

/** Sahifa o'lchami — backend `max_page_size` (100) dan oshmasin.
 *  Notanish qiymat JIM tashlanadi: aks holda `?size=99999` API dan 400
 *  olib, sahifa butunlay yiqilardi. */
function pageSize(raw: string | undefined): string | undefined {
  return raw === "50" || raw === "100" ? raw : undefined;
}

export type AttemptsQuery = {
  cursor?: string;
  verdict?: string;
  language?: string;
  mine?: string;
  username?: string;
  ordering?: string;
  size?: string;
};

/** Urinishlar tab paneli — mavjud oqim, ulashsa bo'ladigan havola bilan.
 *
 *  Eski `/status` sahifasidan ko'chirilgan, farqi faqat manzil:
 *  `/status?...` emas, `?tab=attempts&...`. Manba begonaga ko'rinmaydi —
 *  backend uni faqat egasiga qaytaradi (IDOR himoyasi API'da).
 *  Auth alohida tekshirilmaydi: ro'yxat ochiq, «faqat meniki» filtri
 *  kirgan odamga ko'rinadi (`AttemptFilters` ichida `useSession`).
 *
 *  Filtr/saralash/sahifa o'lchami/qidiruv SERVERDA va URL da — mijozda
 *  filtrlash mumkin emas (kursorli ro'yxat faqat joriy 25 qatorni kesardi).
 */
export async function ProblemAttemptsPanel({
  problem,
  slug,
  query,
  locale,
}: {
  problem: ProblemDetail;
  slug: string;
  query: AttemptsQuery;
  locale: Locale;
}) {
  const { cursor, verdict, language, mine, username, ordering } = query;
  const size = pageSize(query.size);

  const filters = new URLSearchParams();
  if (verdict) filters.set("verdict", verdict);
  if (language) filters.set("language", language);
  if (mine === "true") filters.set("mine", "true");
  if (username) filters.set("username", username);
  if (ordering) filters.set("ordering", ordering);
  if (size) filters.set("page_size", size);
  const apiQuery = filters.toString();

  const page = await api.problemAttempts(
    slug,
    [apiQuery, cursor ? `cursor=${encodeURIComponent(cursor)}` : ""]
      .filter(Boolean)
      .join("&"),
  );

  const nextCursor = page.next
    ? new URL(page.next).searchParams.get("cursor")
    : null;
  const previousCursor = page.previous
    ? new URL(page.previous).searchParams.get("cursor")
    : null;

  const activeCount = [verdict, language, username, mine === "true" ? "1" : ""].filter(
    Boolean,
  ).length;

  const pageHref = (target: string): Route => {
    const params = new URLSearchParams(filters);
    params.set("cursor", target);
    return buildAttemptsHref(slug, Object.fromEntries(params)) as Route;
  };

  const tableQuery = {
    verdict,
    language,
    mine: mine === "true" ? "true" : undefined,
    username,
    ordering,
    size,
  };

  return (
    <AttemptLiveProvider problem={slug}>
    <div className="space-y-6">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h1 className="text-title-sm font-bold rw-strong">
          {problem.code !== null && (
            <span className="mr-2 font-mono text-theme-sm rw-faint tabular-nums">
              #{String(problem.code).padStart(4, "0")}
            </span>
          )}
          {problem.title}
        </h1>
        {activeCount === 0 && (
          <span className="text-theme-sm rw-faint tabular-nums">
            {fill(t(locale, "attempts.total"), { count: problem.attempt_count })}
          </span>
        )}
      </div>

      <AttemptFilters
        slug={slug}
        languages={problem.languages.map((l) => l.code)}
        verdict={verdict}
        language={language}
        mine={mine === "true"}
        username={username}
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
            <p className="mt-1 text-theme-xs rw-faint">
              {activeCount > 0 ? (
                <Link
                  href={buildAttemptsHref(slug, {}) as Route}
                  className="rw-accent-ink"
                >
                  {t(locale, "attempts.clearFilters")}
                </Link>
              ) : (
                t(locale, "attempts.emptyHint")
              )}
            </p>
          </div>
        </Card>
      ) : (
        <Card bodyClassName="p-0">
          <AttemptTable
            slug={slug}
            rows={page.results}
            ordering={ordering}
            query={tableQuery}
          />

          {(previousCursor || nextCursor) && (
            <nav
              aria-label={t(locale, "problem.pagination")}
              className="flex items-center justify-between gap-3 px-5 py-4"
            >
              {previousCursor ? (
                <Link
                  href={pageHref(previousCursor)}
                  rel="prev"
                  className="text-theme-sm rw-dim-2 hover:underline"
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
                  className="text-theme-sm rw-dim-2 hover:underline"
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
