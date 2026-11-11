import type { Metadata, Route } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { MEDAL_COLOR, MEDAL_LABEL, eventPath } from "@/features/olympiads";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api, ApiError, type OlympiadParticipant } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string }> };

async function load(slug: string): Promise<OlympiadParticipant | null> {
  try {
    return await api.olympiadParticipant(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const locale = await getLocale();
  const row = await load(slug);
  return {
    title: row === null ? t(locale, "olympiads.notFound") : row.full_name,
    // Most participants are school pupils: the page is not offered to search
    // engines (personal data, owner decision 2026-11-11).
    robots: { index: false, follow: false },
  };
}

/** A participant's results across the archive (name and country, from official
 *  results). Removed on request from the admin. */
export default async function OlympiadParticipantPage({ params }: Props) {
  const { slug } = await params;
  const locale = await getLocale();
  const person = await load(slug);
  if (person === null) notFound();

  return (
    <article className="mx-auto max-w-3xl space-y-6">
      <nav aria-label={t(locale, "olympiads.breadcrumbs")} className="text-theme-sm rw-dim">
        <Link href={"/olympiads" as Route} className="rw-focus-ring hover:underline">
          {t(locale, "olympiads.title")}
        </Link>
      </nav>
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{person.full_name}</h1>
        {person.country_code && <p className="mt-1 text-theme-sm rw-faint">{person.country_code}</p>}
      </header>
      <Card title={t(locale, "olympiads.results")} bodyClassName="p-0">
        <ul className="rw-divide divide-y">
          {person.results.map((row) => {
            const medal = MEDAL_LABEL[row.medal];
            return (
              <li key={row.event}>
                <Link
                  href={eventPath(row.event) as Route}
                  className="flex min-h-11 flex-wrap items-center gap-3 px-5 py-2.5 transition rw-hover-bg rw-focus-ring"
                >
                  <span className="min-w-0 flex-1 text-theme-sm font-medium rw-strong">
                    {inReaderAlphabet(row.event_title, "uz")}
                  </span>
                  {row.rank !== null && <span className="text-theme-xs tabular-nums rw-dim">#{row.rank}</span>}
                  {medal && <Badge color={MEDAL_COLOR[row.medal] ?? "neutral"}>{t(locale, medal)}</Badge>}
                </Link>
              </li>
            );
          })}
        </ul>
      </Card>
      <p className="text-theme-xs rw-faint">{t(locale, "olympiads.personNote")}</p>
    </article>
  );
}
