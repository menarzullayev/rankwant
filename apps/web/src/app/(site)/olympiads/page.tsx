import type { Metadata, Route } from "next";
import Link from "next/link";

import { EmptyState } from "@/components/ui/EmptyState";
import { EventCard } from "@/features/olympiads";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api, type OlympiadEventCard, type OlympiadSeason } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

const CHIP =
  "inline-flex min-h-9 items-center rw-radius-full border rw-line px-3 text-theme-xs font-medium transition rw-hover-line rw-focus-ring";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return {
    title: t(locale, "olympiads.title"),
    description: t(locale, "olympiads.intro"),
    alternates: { canonical: "/olympiads" },
  };
}

/** Events on a route in the route's own order; the rest after them. */
function byRoute(season: OlympiadSeason): { title: string; description: string; events: OlympiadEventCard[] }[] {
  const placed = new Set<string>();
  const groups = [...season.routes]
    .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
    .map((route) => {
      const events = season.events
        .filter((event) => event.routes.some((m) => m.route_code === route.code))
        .sort((a, b) => {
          const order = (e: OlympiadEventCard) => e.routes.find((m) => m.route_code === route.code)?.order ?? 0;
          return order(a) - order(b);
        });
      for (const event of events) placed.add(event.slug);
      return { title: route.title, description: route.description, events };
    })
    .filter((group) => group.events.length > 0);
  const rest = season.events.filter((event) => !placed.has(event.slug));
  if (rest.length > 0) groups.push({ title: "", description: "", events: rest });
  return groups;
}

/** The olympiad archive (ADR-0062 § 2.6): one season at a time, by its routes —
 *  from the school round to the IOI, EGOI, APIO and the rest. */
export default async function OlympiadsPage({ searchParams }: Props) {
  const locale = await getLocale();
  const seasons = await api.olympiadSeasons().catch((): OlympiadSeason[] => []);
  const wanted = (await searchParams).season;
  const season =
    seasons.find((row) => row.slug === wanted) ?? seasons.find((row) => row.events.some((e) => e.status === "completed")) ?? seasons[0];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "olympiads.title")}</h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">{t(locale, "olympiads.intro")}</p>
      </header>

      {seasons.length > 1 && (
        <nav aria-label={t(locale, "olympiads.seasons")} className="flex flex-wrap gap-2">
          {seasons.map((row) => (
            <Link
              key={row.slug}
              href={`/olympiads?season=${row.slug}` as Route}
              aria-current={row.slug === season?.slug ? "page" : undefined}
              className={`${CHIP} ${row.slug === season?.slug ? "rw-accent-soft rw-accent-ink" : "rw-dim"}`}
            >
              {row.slug}
            </Link>
          ))}
        </nav>
      )}

      {season && (
        <>
          <section>
            <h2 className="text-theme-lg font-semibold rw-strong">{inReaderAlphabet(season.title, "uz")}</h2>
            {season.summary && <p className="mt-1 max-w-3xl text-theme-sm rw-dim">{inReaderAlphabet(season.summary, "uz")}</p>}
          </section>
          {byRoute(season).map((group) => (
            <section key={group.title || "-"} className="space-y-3">
              <h3 className="text-theme-base font-semibold rw-strong">
                {group.title ? inReaderAlphabet(group.title, "uz") : t(locale, "olympiads.otherEvents")}
              </h3>
              {group.description && <p className="max-w-3xl text-theme-sm rw-dim">{inReaderAlphabet(group.description, "uz")}</p>}
              <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {group.events.map((event) => (
                  <li key={event.slug}>
                    <EventCard event={event} locale={locale} />
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </>
      )}

      {!season && <EmptyState variant="card" title={t(locale, "common.empty")} hint={t(locale, "common.emptyHint")} />}

      <p className="text-theme-xs rw-faint">{t(locale, "olympiads.source")}</p>
    </div>
  );
}
