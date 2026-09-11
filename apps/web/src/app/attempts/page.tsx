import Link from "next/link";
import type { Metadata } from "next";

import { Card } from "@/components/ui/Card";
import { UserName } from "@/components/UserName";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { VerdictBadge } from "@/components/VerdictBadge";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "attempts.title") };
}

export default async function AttemptsPage() {
  const locale = await getLocale();
  const data = await api.attempts();
  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "attempts.title")}
      </h1>
      <Card bodyClassName="p-0">
        <Table>
          <THead>
            <TH>#</TH>
            <TH>{t(locale, "standings.user")}</TH>
            <TH>{t(locale, "problems.name")}</TH>
            <TH>{t(locale, "attempts.language")}</TH>
            <TH>{t(locale, "attempts.verdict")}</TH>
            <TH align="right">ms</TH>
            <TH align="right">KB</TH>
            <TH align="right">Vaqt</TH>
          </THead>
          <TBody>
            {data.results.map((a) => (
              <TR key={a.id}>
                <TD className="rw-faint">{a.id}</TD>
                <TD>
                  <UserName username={a.username} title={a.user_title} locale={locale} />
                </TD>
                <TD>
                  <Link
                    href={`/problems/${a.problem}`}
                    className="rw-link-hover"
                  >
                    {a.problem}
                  </Link>
                </TD>
                <TD className="rw-faint">{a.language}</TD>
                <TD>
                  <VerdictBadge verdict={a.verdict} locale={locale} />
                </TD>
                <TD align="right">{a.time_ms}</TD>
                <TD align="right">{a.memory_kb}</TD>
                <TD align="right" className="rw-faint">
                  {new Date(a.created_at).toLocaleTimeString(locale)}
                </TD>
              </TR>
            ))}
            {data.results.length === 0 && (
              <EmptyRow colSpan={8}>{t(locale, "empty")}</EmptyRow>
            )}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
