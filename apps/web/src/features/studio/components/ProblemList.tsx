import type { Route } from "next";
import Link from "next/link";

import { numericStamp } from "@rankwant/shared/format";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { fill, t, type Locale, type MessageKey } from "@/i18n/messages";

import {
  STUDIO_DRAFT_LIMIT,
  draftStatus,
  type DraftStatus,
  type MineProblem,
} from "../api/problems";

const STATUS: Record<DraftStatus, { key: MessageKey; color: BadgeColor }> = {
  draft: { key: "studio.status.draft", color: "neutral" },
  review: { key: "studio.status.review", color: "warning" },
  public: { key: "studio.status.public", color: "success" },
};

export function StatusBadge({ problem, locale }: { problem: MineProblem; locale: Locale }) {
  const status = STATUS[draftStatus(problem)];
  return <Badge color={status.color}>{t(locale, status.key)}</Badge>;
}

/** The author's problems. Rendered on the server: it reads nothing but the
 *  rows, and every action lives on the problem's own page. */
export function ProblemList({ rows, locale }: { rows: MineProblem[]; locale: Locale }) {
  const drafts = rows.filter((row) => !row.is_public).length;
  const full = drafts >= STUDIO_DRAFT_LIMIT;
  const create = (
    <ButtonLink href={"/studio/problems/new" as Route}>{t(locale, "studio.problems.new")}</ButtonLink>
  );

  return (
    <div className="space-y-4">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-title-sm font-bold rw-strong">{t(locale, "studio.nav.problems")}</h1>
          <p className="mt-1 max-w-2xl text-theme-sm rw-dim">{t(locale, "studio.problems.intro")}</p>
        </div>
        {rows.length > 0 && !full && create}
      </header>

      {rows.length === 0 ? (
        <EmptyState
          variant="card"
          title={t(locale, "studio.problems.empty")}
          hint={t(locale, "studio.problems.emptyHint")}
          action={{ label: t(locale, "studio.problems.new"), href: "/studio/problems/new" }}
        />
      ) : (
        <>
          <Table>
            <THead>
              <TH>{t(locale, "studio.col.problem")}</TH>
              <TH className="hidden @lg:table-cell">{t(locale, "studio.col.difficulty")}</TH>
              <TH className="hidden @xl:table-cell">{t(locale, "studio.col.tests")}</TH>
              <TH>{t(locale, "studio.col.status")}</TH>
              <TH className="hidden @2xl:table-cell">{t(locale, "studio.col.updated")}</TH>
            </THead>
            <TBody>
              {rows.map((row) => (
                <TR key={row.slug}>
                  <TD>
                    <Link
                      href={`/studio/problems/${encodeURIComponent(row.slug)}` as Route}
                      className="font-medium rw-strong hover:underline"
                    >
                      {row.title}
                    </Link>
                    <span className="block font-mono text-theme-xs rw-faint">{row.slug}</span>
                  </TD>
                  <TD className="hidden tabular-nums @lg:table-cell">{row.difficulty}</TD>
                  <TD className="hidden @xl:table-cell">
                    {fill(t(locale, "studio.tests.summary"), {
                      samples: row.sample_count,
                      hidden: row.hidden_count,
                    })}
                  </TD>
                  <TD>
                    <StatusBadge problem={row} locale={locale} />
                  </TD>
                  <TD className="hidden whitespace-nowrap font-mono text-theme-xs rw-dim @2xl:table-cell">
                    {numericStamp(row.updated_at)}
                  </TD>
                </TR>
              ))}
            </TBody>
          </Table>
          <p className="text-theme-xs rw-faint">
            {fill(t(locale, full ? "studio.problems.full" : "studio.problems.count"), {
              count: drafts,
              limit: STUDIO_DRAFT_LIMIT,
            })}
          </p>
        </>
      )}
    </div>
  );
}
