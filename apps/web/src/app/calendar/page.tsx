import Link from "next/link";
import type { Metadata } from "next";

import { Badge, type BadgeColor } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { api, type CalendarEvent } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "calendar.title") };
}

const KIND: Record<
  CalendarEvent["kind"],
  { color: BadgeColor; label: string; base: string }
> = {
  contest: { color: "brand", label: "nav.contests", base: "/contests" },
  arena: { color: "warning", label: "nav.arena", base: "/arena" },
  tournament: { color: "info", label: "nav.tournaments", base: "/tournaments" },
  hackathon: { color: "success", label: "nav.hackathons", base: "/hackathons" },
  duel: { color: "error", label: "nav.duels", base: "/duels" },
};

function Row({
  e,
  locale,
}: {
  e: CalendarEvent;
  locale: typeof DEFAULT_LOCALE;
}) {
  const k = KIND[e.kind];
  const start = new Date(e.start_at);
  return (
    <li className="flex items-center gap-4 px-5 py-3">
      <div className="w-14 shrink-0 text-center">
        <p className="text-title-sm font-bold leading-none rw-strong">
          {start.getDate()}
        </p>
        <p className="text-theme-xs rw-faint uppercase">
          {start.toLocaleDateString(locale, { month: "short" })}
        </p>
      </div>
      <div className="min-w-0 flex-1">
        <Link
          href={`${k.base}/${e.slug}` as `/contests/${string}`}
          className="block truncate font-medium rw-strong rw-link-hover"
        >
          {e.title}
        </Link>
        <p className="text-theme-xs rw-faint">
          {start.toLocaleTimeString(locale, {
            hour: "2-digit",
            minute: "2-digit",
          })}{" "}
          —{" "}
          {new Date(e.end_at).toLocaleString(locale, {
            day: "numeric",
            month: "short",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
      <Badge color={k.color}>{t(locale, k.label)}</Badge>
      {e.is_rated && <Badge color="brand">{t(locale, "contests.rated")}</Badge>}
    </li>
  );
}

/** Render'dan tashqarida: React qoidasi komponent ichida `Date.now` ni taqiqlaydi. */
function splitByNow(results: CalendarEvent[]) {
  const now = Date.now();
  return {
    upcoming: results.filter((e) => new Date(e.end_at).getTime() >= now),
    past: results.filter((e) => new Date(e.end_at).getTime() < now).reverse(),
  };
}

export default async function CalendarPage() {
  const locale = await getLocale();
  const { results } = await api.calendar();
  const { upcoming, past } = splitByNow(results);

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "calendar.title")}
      </h1>
      <Card title={t(locale, "calendar.upcoming")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {upcoming.map((e) => (
            <Row key={`${e.kind}-${e.slug}`} e={e} locale={locale} />
          ))}
          {upcoming.length === 0 && (
            <li className="px-5 py-8 text-center text-theme-sm rw-faint">
              {t(locale, "common.empty")}
            </li>
          )}
        </ul>
      </Card>
      {past.length > 0 && (
        <Card title={t(locale, "calendar.past")} bodyClassName="p-0">
          <ul className="divide-y rw-divide">
            {past.map((e) => (
              <Row key={`${e.kind}-${e.slug}`} e={e} locale={locale} />
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
