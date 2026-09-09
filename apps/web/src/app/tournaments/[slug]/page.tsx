import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Markdown } from "@/components/Markdown";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api, ApiError } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    return { title: (await api.tournament(slug)).title };
  } catch {
    return { title: "404" };
  }
}

export default async function TournamentPage({ params }: Props) {
  const { slug } = await params;
  const locale = await getLocale();
  let tn;
  try {
    tn = await api.tournament(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  const { results } = await api.tournamentStandings(slug);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{tn.title}</h1>
        <p className="mt-2 text-theme-xs rw-faint">
          {new Date(tn.start_at).toLocaleDateString(locale)} —{" "}
          {new Date(tn.end_at).toLocaleDateString(locale)}
        </p>
      </header>
      {tn.description && (
        <Card>
          <Markdown>{tn.description}</Markdown>
        </Card>
      )}

      <Card title={t(locale, "tournament.stages")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {tn.stages.map((s) => (
            <li key={s.order} className="flex items-center gap-4 px-5 py-3">
              <span className="w-8 text-theme-sm font-semibold rw-faint">
                {s.order}
              </span>
              <div className="min-w-0 flex-1">
                <Link
                  href={`/contests/${s.contest}`}
                  className="font-medium rw-strong rw-link-hover"
                >
                  {s.title}
                </Link>
                <p className="text-theme-xs rw-faint">
                  {s.contest_title} ·{" "}
                  {new Date(s.start_at).toLocaleString(locale)}
                </p>
              </div>
              {s.weight > 1 && <Badge color="brand">×{s.weight}</Badge>}
              <Badge color={s.is_finished ? "neutral" : "info"}>
                {t(
                  locale,
                  s.is_finished ? "contests.finished" : "contests.upcoming",
                )}
              </Badge>
            </li>
          ))}
        </ul>
      </Card>

      <Card title={t(locale, "standings.title")} bodyClassName="p-0">
        <p className="px-5 pt-3 text-theme-xs rw-faint">
          {t(locale, "tournament.formula")}
        </p>
        <Table>
          <THead>
            <TH>#</TH>
            <TH>{t(locale, "standings.user")}</TH>
            <TH align="right">{t(locale, "tournament.points")}</TH>
            <TH align="right">{t(locale, "standings.solved")}</TH>
            <TH align="right">{t(locale, "tournament.stages")}</TH>
          </THead>
          <TBody>
            {results.map((r) => (
              <TR key={r.username}>
                <TD className="font-semibold">{r.rank}</TD>
                <TD>
                  <Link
                    href={`/users/${r.username}`}
                    className="font-medium rw-link-hover"
                  >
                    {r.display_name || r.username}
                  </Link>
                </TD>
                <TD align="right" className="font-semibold">
                  {r.points}
                </TD>
                <TD align="right">{r.solved_total}</TD>
                <TD align="right" className="rw-faint">
                  {r.stages_played}
                </TD>
              </TR>
            ))}
            {results.length === 0 && (
              <EmptyRow colSpan={5}>{t(locale, "empty")}</EmptyRow>
            )}
          </TBody>
        </Table>
      </Card>
    </div>
  );
}
