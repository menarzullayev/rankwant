import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { ProblemTabs } from "@/features/problems";
import { Card } from "@/components/ui/Card";
import { fill, t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { AttemptFilters, AttemptTable } from "@/features/submissions";
import { api, ApiError } from "@/lib/api";

type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{
    cursor?: string;
    verdict?: string;
    language?: string;
    mine?: string;
    username?: string;
    ordering?: string;
    size?: string;
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

/** Sahifa o'lchami — backend `max_page_size` (100) dan oshmasin.
 *  Notanish qiymat JIM tashlanadi: aks holda `?size=99999` API dan 400
 *  olib, sahifa butunlay yiqilardi. */
function pageSize(raw: string | undefined): string | undefined {
  return raw === "50" || raw === "100" ? raw : undefined;
}

/** Masalaning barcha urinishlari — Codeforces'ning STATUS sahifasi.
 *
 * Panel tabida oxirgi o'ntasi ko'rinadi; bu yerda to'liq oqim, ulashsa
 * bo'ladigan havola bilan. Manba begonaga ko'rinmaydi — backend uni
 * faqat egasiga qaytaradi.
 *
 * ⚠️ Filtr, saralash, sahifa o'lchami va qidiruv — hammasi SERVERDA
 * qo'llanadi va URL da saqlanadi. Mijozda filtrlash mumkin emas: ro'yxat
 * kursorli, ya'ni u faqat joriy 25 qatorni kesib, qolganini yashirardi.
 */
export default async function ProblemStatusPage({
  params,
  searchParams,
}: Props) {
  const locale = await getLocale();
  const { slug } = await params;
  const { cursor, verdict, language, mine, username, ordering } =
    await searchParams;
  const size = pageSize((await searchParams).size);

  const filters = new URLSearchParams();
  if (verdict) filters.set("verdict", verdict);
  if (language) filters.set("language", language);
  if (mine === "true") filters.set("mine", "true");
  if (username) filters.set("username", username);
  if (ordering) filters.set("ordering", ordering);
  if (size) filters.set("page_size", size);
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

  //: Kursorli sahifalash: `next` to'liq URL, bizga faqat kursor kerak.
  const nextCursor = page.next
    ? new URL(page.next).searchParams.get("cursor")
    : null;
  const previousCursor = page.previous
    ? new URL(page.previous).searchParams.get("cursor")
    : null;

  /** Faol filtrlar soni — yopishqoq qatordagi ko'rsatkich uchun (S11). */
  const activeCount = [verdict, language, username, mine === "true" ? "1" : ""].filter(
    Boolean,
  ).length;

  /** Ro'yxat havolasi — filtrlar saqlanadi, kursor yangilanadi. */
  const pageHref = (nextCursor: string): Route => {
    const next = new URLSearchParams(filters);
    next.set("cursor", nextCursor);
    return `/problems/${slug}/status?${next}` as Route;
  };

  /** Boshqa filtrlar — jadval saralashda saqlanadi. */
  const tableQuery = {
    verdict,
    language,
    mine: mine === "true" ? "true" : undefined,
    username,
    ordering,
    size,
  };

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
        {/* Jami son (S13). Filtrlangan holatda KO'RSATILMAYDI: kursorli
            sahifalashda jami son yo'q va «20+» kabi taxmin yolg'on
            aniqlik bo'lardi — sababni faol filtr qatori aytadi. */}
        {activeCount === 0 && (
          <span className="text-theme-sm rw-faint tabular-nums">
            {fill(t(locale, "attempts.total"), { count: problem.attempt_count })}
          </span>
        )}
      </div>

      <ProblemTabs slug={slug} current="status" />

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
          {/* Bo'sh holat IKKI XIL (S19): filtrsiz — hali urinish yo'q;
              filtrli — tupik, va undan chiqish yo'li ko'rsatilishi shart,
              aks holda foydalanuvchi nima bo'lganini tushunmaydi. */}
          <div className="px-5 py-12 text-center">
            <p className="text-theme-sm rw-strong">
              {activeCount > 0
                ? t(locale, "attempts.emptyFilteredTitle")
                : t(locale, "attempts.emptyTitle")}
            </p>
            <p className="mt-1 text-theme-xs rw-faint">
              {activeCount > 0 ? (
                <Link
                  href={`/problems/${slug}/status` as Route}
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
  );
}
