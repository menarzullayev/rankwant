import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { dateTime, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.arena") };
}

export default async function ArenaListPage() {
  const locale = await getLocale();
  const data = await api.arenas();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.arena")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          {t(locale, "arena.intro")}
        </p>
      </header>
      <ul className="grid gap-4 md:grid-cols-2">
        {data.results.map((a) => (
          <li key={a.slug}>
            <ListCard
              href={`/arena/${a.slug}`}
              title={a.title}
              summary={a.description}
              meta={
                <>
                  <Badge
                    color={
                      a.is_running
                        ? "success"
                        : a.is_finished
                          ? "neutral"
                          : "info"
                    }
                  >
                    {t(
                      locale,
                      a.is_running
                        ? "contests.running"
                        : a.is_finished
                          ? "contests.finished"
                          : "contests.upcoming",
                    )}
                  </Badge>
                  <Badge>
                    {a.question_count} {t(locale, "quiz.questions")} ·{" "}
                    {a.seconds_per_question}
                    {t(locale, "arena.perQuestion")}
                  </Badge>
                  <Badge color="brand">{a.participant_count} 👤</Badge>
                  <span>{dateTime(a.start_at, locale)}</span>
                </>
              }
            />
          </li>
        ))}
      </ul>
      {data.count === 0 && (
        <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
      )}
    </div>
  );
}
