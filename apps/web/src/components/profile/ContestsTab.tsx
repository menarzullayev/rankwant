import type { Route } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Pager } from "@/components/ui/Pager";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { t, type Locale } from "@/i18n/messages";
import { api, type ContestRow } from "@/lib/api";
import { formatDate, formatDuration } from "@/lib/format";
import { SectionHint } from "./SectionHint";

const PAGE_SIZE = 25;

function Rating({ row }: { row: ContestRow }) {
  if (!row.rating) return <span className="rw-faint">—</span>;
  const { before, after, delta } = row.rating;
  return (
    <span className="tabular-nums">
      {before !== null && after !== null && (
        <span className="rw-dim">
          {before} → {after}{" "}
        </span>
      )}
      <span className={`font-semibold ${delta >= 0 ? "rw-ok-ink" : "rw-bad-ink"}`}>
        {delta > 0 ? "+" : ""}
        {delta}
      </span>
    </span>
  );
}

/** Qatnashgan musobaqalar — o'rin (teng natija oralig'i bilan), reyting o'zgarishi, hajm. */
export async function ContestsTab({
  username,
  query,
  locale,
}: {
  username: string;
  query: { q?: string; page?: string };
  locale: Locale;
}) {
  const page = Math.max(1, Number(query.page) || 1);
  const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
  if (query.q) params.set("q", query.q);
  const data = await api.userContests(username, `?${params}`);
  const base = `/users/${username}/musobaqalar`;

  return (
    <Card bodyClassName="p-0">
      <div className="space-y-3 border-b rw-line px-5 py-4">
        <SectionHint>{t(locale, "profile.contestsHint")}</SectionHint>
        <form action={base}>
          <label className="block max-w-sm">
            <span className="sr-only">{t(locale, "profile.search")}</span>
            <input
              type="search"
              name="q"
              defaultValue={query.q ?? ""}
              placeholder={t(locale, "profile.searchContests")}
              className="h-9 w-full rw-radius-sm border rw-line px-3 text-theme-sm rw-strong rw-field-bg rw-focus-ring rw-placeholder"
            />
          </label>
        </form>
      </div>
      <Table>
        <THead>
          <TH>{t(locale, "profile.contestCol")}</TH>
          <TH align="right">{t(locale, "standings.rank")}</TH>
          <TH align="right">{t(locale, "profile.ratingChange")}</TH>
          <TH align="right">{t(locale, "profile.problemsCol")}</TH>
          <TH align="right">{t(locale, "profile.participants")}</TH>
          <TH>{t(locale, "profile.startCol")}</TH>
          <TH align="right">{t(locale, "profile.durationCol")}</TH>
          <TH>{t(locale, "profile.kindCol")}</TH>
        </THead>
        <TBody>
          {data.results.map((row) => (
            <TR key={row.slug}>
              <TD>
                <Link href={`/contests/${row.slug}` as Route} className="font-medium rw-strong rw-link-hover">
                  {row.title}
                </Link>
              </TD>
              <TD align="right" className="tabular-nums rw-strong">
                {row.rank_from === row.rank_to ? row.rank_from : `${row.rank_from}–${row.rank_to}`}
              </TD>
              <TD align="right">
                <Rating row={row} />
              </TD>
              <TD align="right" className="tabular-nums">
                {row.problems}
              </TD>
              <TD align="right" className="tabular-nums">
                {row.participants}
              </TD>
              <TD className="rw-dim">{formatDate(row.start_at, locale)}</TD>
              <TD align="right" className="tabular-nums rw-dim">
                {formatDuration(row.duration_min)}
              </TD>
              <TD>
                <Badge color={row.virtual ? "neutral" : "brand"}>
                  {t(locale, row.virtual ? "profile.virtual" : "profile.official")}
                </Badge>
              </TD>
            </TR>
          ))}
          {data.results.length === 0 && (
            <EmptyRow colSpan={8}>{t(locale, "profile.contestsEmpty")}</EmptyRow>
          )}
        </TBody>
      </Table>
      <Pager
        page={page}
        count={data.count}
        pageSize={PAGE_SIZE}
        href={(to) =>
          `${base}?${new URLSearchParams({ ...(query.q ? { q: query.q } : {}), page: String(to) })}` as Route
        }
      />
    </Card>
  );
}
