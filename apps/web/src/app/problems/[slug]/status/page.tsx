import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ProblemTabs } from "@/components/ProblemTabs";
import { VerdictBadge } from "@/components/VerdictBadge";
import { Card } from "@/components/ui/Card";
import { dateTime, fill, t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { AttemptFilters } from "@/components/AttemptFilters";
import { api, ApiError } from "@/lib/api";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{
    cursor?: string;
    verdict?: string;
    language?: string;
    mine?: string;
  }>;
};

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: Pick<Props, "params">): Promise<Metadata> {
  const locale = await getLocale();
  const { slug } = await params;
  return { title: fill(t(locale, "problem.status.title"), { slug }) };
}

/** Masalaning barcha urinishlari — Codeforces'ning STATUS sahifasi.
 *
 * Panel tabida oxirgi o'ntasi ko'rinadi; bu yerda to'liq oqim, ulashsa
 * bo'ladigan havola bilan. Manba begonaga ko'rinmaydi — backend uni
 * faqat egasiga qaytaradi. */
export default async function ProblemStatusPage({
  params,
  searchParams,
}: Props) {
  const locale = await getLocale();
  const { slug } = await params;
  const { cursor, verdict, language, mine } = await searchParams;

  // Filtrlar serverda qo'llanadi — ro'yxat kursorli, ya'ni mijozda
  // filtrlash faqat joriy sahifani kesib, qolganini yashirardi.
  const filters = new URLSearchParams();
  if (verdict) filters.set("verdict", verdict);
  if (language) filters.set("language", language);
  if (mine === "true") filters.set("mine", "true");
  const query = filters.toString();

  let problem;
  let page;
  try {
    [problem, page] = await Promise.all([
      api.problem(slug),
      api.problemAttempts(
        slug,
        [query, cursor ? `cursor=${encodeURIComponent(cursor)}` : ""]
          .filter(Boolean)
          .join("&"),
      ),
    ]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  // Kursorli sahifalash: `next` to'liq URL, bizga faqat kursor kerak.
  const nextCursor = page.next
    ? new URL(page.next).searchParams.get("cursor")
    : null;
  const previousCursor = page.previous
    ? new URL(page.previous).searchParams.get("cursor")
    : null;

  return (
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
      </div>

      <ProblemTabs slug={slug} current="status" />

      <AttemptFilters
        slug={slug}
        languages={problem.languages.map((l) => l.code)}
        verdict={verdict}
        language={language}
        mine={mine === "true"}
      />

      <Card bodyClassName="p-0">
        <Table>
          <THead>
            <TH>Foydalanuvchi</TH>
            <TH>Verdikt</TH>
            <TH>Til</TH>
            <TH align="right">Vaqt</TH>
            <TH align="right" className="hidden sm:table-cell">
              Xotira
            </TH>
            <TH align="right" className="hidden lg:table-cell">
              Hajm
            </TH>
            <TH align="right" className="hidden md:table-cell">
              Sana
            </TH>
          </THead>
          <TBody>
            {page.results.map((attempt) => (
              <TR key={attempt.id}>
                <TD>
                  <Link
                    href={`/users/${attempt.username}`}
                    className="font-medium rw-strong rw-link-hover"
                  >
                    {attempt.username}
                  </Link>
                </TD>
                <TD>
                  <VerdictBadge verdict={attempt.verdict} locale={locale} />
                </TD>
                <TD className="rw-dim">{attempt.language}</TD>
                <TD align="right" className="rw-faint tabular-nums">
                  {attempt.time_ms} ms
                </TD>
                <TD
                  align="right"
                  className="hidden rw-faint tabular-nums sm:table-cell"
                >
                  {Math.round(attempt.memory_kb / 1024)} MB
                </TD>
                <TD
                  align="right"
                  className="hidden rw-faint tabular-nums lg:table-cell"
                >
                  {attempt.source_size} B
                </TD>
                <TD align="right" className="hidden rw-faint md:table-cell">
                  <time dateTime={attempt.created_at}>
                    {dateTime(attempt.created_at, locale)}
                  </time>
                </TD>
              </TR>
            ))}
            {page.results.length === 0 && (
              <EmptyRow colSpan={7}>
                {query
                  ? t(locale, "problem.noAttemptMatch")
                  : t(locale, "problem.noAttemptsYet")}
              </EmptyRow>
            )}
          </TBody>
        </Table>

        {(previousCursor || nextCursor) && (
          <nav
            aria-label={t(locale, "problem.pagination")}
            className="flex items-center justify-between gap-3 px-5 py-4"
          >
            {previousCursor ? (
              <Link
                href={
                  `/problems/${slug}/status?cursor=${encodeURIComponent(previousCursor)}` as Route
                }
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
                href={
                  `/problems/${slug}/status?cursor=${encodeURIComponent(nextCursor)}` as Route
                }
                rel="next"
                className="text-theme-sm rw-dim-2 hover:underline"
              >
                {t(locale, "problem.nextPage")}
              </Link>
            )}
          </nav>
        )}
      </Card>
    </div>
  );
}
