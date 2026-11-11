import type { Route } from "next";
import Link from "next/link";

import { numericStamp } from "@rankwant/shared/format";

import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { fill, t, type Locale } from "@/i18n/messages";

import { quotaFull, type Quota } from "@/lib/quotas";

import { type MineContest } from "../api/contests";

export function ContestStatus({ contest, locale }: { contest: MineContest; locale: Locale }) {
  return contest.is_public ? (
    <Badge color="success">{t(locale, "studio.status.public")}</Badge>
  ) : (
    <Badge color="neutral">{t(locale, "studio.status.draft")}</Badge>
  );
}

/** The organizer's contests. Rendered on the server, like the problem list;
 *  the plan's quota counts published contests too (ADR-0061 § 2). */
export function ContestList({
  rows,
  quota,
  locale,
}: {
  rows: MineContest[];
  quota: Quota;
  locale: Locale;
}) {
  const full = quotaFull(quota);

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-title-sm font-bold rw-strong">{t(locale, "studio.nav.contests")}</h1>
          <p className="mt-1 max-w-2xl text-theme-sm rw-dim">{t(locale, "studio.contests.intro")}</p>
        </div>
        {rows.length > 0 && !full && (
          <ButtonLink href={"/studio/contests/new" as Route}>{t(locale, "studio.contests.new")}</ButtonLink>
        )}
      </header>

      {rows.length === 0 ? (
        <EmptyState
          variant="card"
          title={t(locale, "studio.contests.empty")}
          hint={t(locale, "studio.contests.emptyHint")}
          action={{ label: t(locale, "studio.contests.new"), href: "/studio/contests/new" }}
        />
      ) : (
        <>
          <Table>
            <THead>
              <TH>{t(locale, "studio.col.contest")}</TH>
              <TH className="hidden @lg:table-cell">{t(locale, "studio.col.start")}</TH>
              <TH className="hidden @xl:table-cell">{t(locale, "studio.col.problems")}</TH>
              <TH className="hidden @xl:table-cell">{t(locale, "studio.col.participants")}</TH>
              <TH>{t(locale, "studio.col.status")}</TH>
            </THead>
            <TBody>
              {rows.map((row) => (
                <TR key={row.slug}>
                  <TD>
                    <Link
                      href={`/studio/contests/${encodeURIComponent(row.slug)}` as Route}
                      className="font-medium rw-strong hover:underline"
                    >
                      {row.title}
                    </Link>
                    <span className="block font-mono text-theme-xs rw-faint">{row.slug}</span>
                  </TD>
                  <TD className="hidden whitespace-nowrap font-mono text-theme-xs rw-dim @lg:table-cell">
                    {numericStamp(row.start_at)}
                  </TD>
                  <TD className="hidden tabular-nums @xl:table-cell">{row.problems.length}</TD>
                  <TD className="hidden tabular-nums @xl:table-cell">{row.participant_count}</TD>
                  <TD>
                    <ContestStatus contest={row} locale={locale} />
                  </TD>
                </TR>
              ))}
            </TBody>
          </Table>
          {quota.limit !== null && (
            <p className="text-theme-xs rw-faint">
              {fill(t(locale, full ? "studio.contests.full" : "studio.contests.count"), {
                count: quota.used,
                limit: quota.limit,
              })}
            </p>
          )}
        </>
      )}
    </div>
  );
}
