import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { date, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.tournaments") };
}

export default async function TournamentsPage() {
  const locale = await getLocale();
  const data = await api.tournaments();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.tournaments")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          Bir nechta musobaqadan iborat mavsum.{" "}
          {t(locale, "tournament.formula")}
        </p>
      </header>
      <ul className="grid gap-4 md:grid-cols-2">
        {data.results.map((tn) => (
          <li key={tn.slug}>
            <ListCard
              href={`/tournaments/${tn.slug}`}
              title={tn.title}
              summary={tn.description}
              meta={
                <>
                  <Badge
                    color={
                      tn.is_running
                        ? "success"
                        : tn.is_finished
                          ? "neutral"
                          : "info"
                    }
                  >
                    {t(
                      locale,
                      tn.is_running
                        ? "contests.running"
                        : tn.is_finished
                          ? "contests.finished"
                          : "contests.upcoming",
                    )}
                  </Badge>
                  <Badge>
                    {tn.stage_count}{" "}
                    {t(locale, "tournament.stages").toLowerCase()}
                  </Badge>
                  <span>
                    {date(tn.start_at, locale)} —{" "}
                    {date(tn.end_at, locale)}
                  </span>
                </>
              }
            />
          </li>
        ))}
      </ul>
      {data.count === 0 && (
        <p className="text-theme-sm rw-faint">{t(locale, "common.empty")}</p>
      )}
    </div>
  );
}
