import type { Metadata, Route } from "next";
import Link from "next/link";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { getLocale } from "@/i18n/server";
import { date, t, type MessageKey } from "@/i18n/messages";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.nav.reports"), robots: { index: false } };
}

type ContentReport = {
  kind: "problem" | "entry" | "comment";
  title: string;
  link: string;
  reason: string;
  note: string;
  status: "open" | "accepted" | "rejected";
  created_at: string;
};

const KIND: Record<ContentReport["kind"], MessageKey> = {
  problem: "myContent.kind.problem",
  entry: "myContent.kind.entry",
  comment: "myContent.kind.comment",
};

const STATUS: Record<ContentReport["status"], { key: MessageKey; color: BadgeColor }> = {
  open: { key: "myContent.status.open", color: "warning" },
  accepted: { key: "myContent.status.accepted", color: "success" },
  rejected: { key: "myContent.status.rejected", color: "neutral" },
};

/** A problem report's reason uses the problem keys, a community one the discussion keys. */
function reasonKey(row: ContentReport): MessageKey {
  return (row.kind === "problem" ? `report.reason.${row.reason}` : `discussion.reason.${row.reason}`) as MessageKey;
}

/** "My content" (decision 2026-11-11 ④): reports about what the reader wrote —
 *  problems, blog entries, comments. The reporter is not named. */
export default async function MyContentPage() {
  await requireUser("/studio/reports");
  const locale = await getLocale();
  const rows = await getWithSession<ContentReport[]>("/me/content-reports/");

  return (
    <div className="space-y-4">
      <div className="space-y-1">
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "studio.nav.reports")}</h1>
        <p className="text-theme-sm rw-dim">{t(locale, "myContent.hint")}</p>
      </div>
      <Card bodyClassName="p-0">
        <Table>
          <THead>
            <TH>{t(locale, "myContent.what")}</TH>
            <TH>{t(locale, "myContent.reason")}</TH>
            <TH className="hidden @xl:table-cell">{t(locale, "myContent.status")}</TH>
            <TH align="right" className="hidden @xl:table-cell">
              {t(locale, "myContent.date")}
            </TH>
          </THead>
          <TBody>
            {rows.length === 0 ? (
              <EmptyRow colSpan={4}>{t(locale, "myContent.empty")}</EmptyRow>
            ) : (
              rows.map((row, i) => (
                <TR key={`${row.kind}-${row.link}-${i}`}>
                  <TD>
                    <span className="block text-theme-xs rw-faint">{t(locale, KIND[row.kind])}</span>
                    {row.link ? (
                      <Link href={row.link as Route} className="line-clamp-2 rw-link-hover rw-strong">
                        {row.title}
                      </Link>
                    ) : (
                      <span className="line-clamp-2 rw-strong">{row.title}</span>
                    )}
                  </TD>
                  <TD>
                    <span className="block">{t(locale, reasonKey(row))}</span>
                    {row.note && <span className="block text-theme-xs rw-dim">{row.note}</span>}
                    <span className="mt-1 block @xl:hidden">
                      <Badge color={STATUS[row.status].color}>{t(locale, STATUS[row.status].key)}</Badge>
                    </span>
                  </TD>
                  <TD className="hidden @xl:table-cell">
                    <Badge color={STATUS[row.status].color}>{t(locale, STATUS[row.status].key)}</Badge>
                  </TD>
                  <TD align="right" className="hidden tabular-nums rw-faint @xl:table-cell">
                    {date(row.created_at, locale)}
                  </TD>
                </TR>
              ))
            )}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
