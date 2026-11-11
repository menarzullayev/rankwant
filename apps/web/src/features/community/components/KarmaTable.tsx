import type { Route } from "next";
import Link from "next/link";

import { UserName } from "@/components/ui/Identity/UserName";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { fill, t, type Locale } from "@/i18n/messages";

import type { KarmaRow } from "../api";

/** People by karma (decision 2026-11-11 ③): the users table's karma board. */
export function KarmaTable({ rows, locale }: { rows: KarmaRow[]; locale: Locale }) {
  return (
    <Table>
      <THead>
        <TH>#</TH>
        <TH>{t(locale, "standings.user")}</TH>
        <TH align="right">{t(locale, "karma.title")}</TH>
        <TH align="right" className="hidden @xl:table-cell">
          {t(locale, "karma.entries")}
        </TH>
      </THead>
      <TBody>
        {rows.length === 0 ? (
          <EmptyRow colSpan={4}>{t(locale, "karma.empty")}</EmptyRow>
        ) : (
          rows.map((row, i) => (
            <TR key={row.user.username}>
              <TD className="tabular-nums rw-faint">{i + 1}</TD>
              <TD>
                <UserName
                  username={row.user.username}
                  name={row.user.display_name}
                  title={row.user.title}
                  locale={locale}
                />
              </TD>
              <TD align="right" className="font-bold tabular-nums rw-ok-ink">
                +{row.karma}
              </TD>
              <TD align="right" className="hidden tabular-nums @xl:table-cell">
                <Link
                  href={`/blogs?author=${encodeURIComponent(row.user.username)}` as Route}
                  className="rw-link-hover"
                >
                  {row.entries}
                </Link>
              </TD>
            </TR>
          ))
        )}
      </TBody>
    </Table>
  );
}

/** "Active authors" beside the blog feed: votes of the last 30 days. */
export function ActiveAuthors({ rows, locale }: { rows: KarmaRow[]; locale: Locale }) {
  if (rows.length === 0) return null;
  return (
    <section aria-labelledby="active-authors" className="space-y-3">
      <h2 id="active-authors" className="text-theme-sm font-semibold rw-strong">
        {t(locale, "karma.active")}
      </h2>
      <ol className="space-y-2">
        {rows.map((row) => (
          <li key={row.user.username} className="flex items-baseline justify-between gap-2 text-theme-sm">
            <UserName
              username={row.user.username}
              name={row.user.display_name}
              title={row.user.title}
              locale={locale}
              className="min-w-0 truncate"
            />
            <span className="shrink-0 text-theme-xs tabular-nums rw-ok-ink">
              {fill(t(locale, "karma.points"), { count: row.points })}
            </span>
          </li>
        ))}
      </ol>
    </section>
  );
}
