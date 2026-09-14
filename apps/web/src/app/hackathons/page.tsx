import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { dateTime, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.hackathons") };
}

export default async function HackathonsPage() {
  const locale = await getLocale();
  const data = await api.hackathons();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.hackathons")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          {t(locale, "hackathons.intro")}
        </p>
      </header>
      <ul className="grid gap-4 md:grid-cols-2">
        {data.results.map((h) => (
          <li key={h.slug}>
            <ListCard
              href={`/hackathons/${h.slug}`}
              title={h.title}
              summary={h.description.slice(0, 160)}
              meta={
                <>
                  <Badge
                    color={
                      h.accepts_submissions
                        ? "success"
                        : h.is_finished
                          ? "neutral"
                          : "info"
                    }
                  >
                    {h.accepts_submissions
                      ? t(locale, "contests.running")
                      : h.is_finished
                        ? t(locale, "contests.finished")
                        : t(locale, "contests.upcoming")}
                  </Badge>
                  <Badge>
                    {h.submission_count}{" "}
                    {t(locale, "hackathon.entries").toLowerCase()}
                  </Badge>
                  <span>
                    {t(locale, "hackathon.deadline")}:{" "}
                    {dateTime(h.submission_deadline, locale)}
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
