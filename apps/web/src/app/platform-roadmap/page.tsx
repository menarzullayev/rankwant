import type { Metadata, Route } from "next";
import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { excerpt } from "@/components/Markdown";
import { RoadmapStatusBadge } from "@/components/RoadmapStatusBadge";
import { RoadmapSuggest } from "@/components/RoadmapSuggest";
import { RoadmapVote } from "@/components/RoadmapVote";
import { getLocale } from "@/i18n/server";
import { date, fill, t, type Locale } from "@/i18n/messages";
import {
  api,
  ROADMAP_COLUMNS,
  type RoadmapItem,
  type RoadmapStatus,
} from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return {
    title: t(locale, "roadmap.title"),
    description: t(locale, "roadmap.lead"),
  };
}

/** Kanban uchun hamma band kerak — sahifalangan ro'yxat ustunlarni
 *  to'ldirmay qo'yardi. `StandardPagination` ning eng yuqori chegarasi. */
const BOARD_SIZE = 100;

/** Bitta karta — taxtada ham, "mening takliflarim" ro'yxatida ham. */
function RoadmapCard({ item, locale }: { item: RoadmapItem; locale: Locale }) {
  return (
    <article className="rw-panel p-4">
      <div className="flex items-start gap-3">
        <RoadmapVote
          id={item.id}
          initialVoted={item.has_voted}
          initialCount={item.vote_count}
          compact
        />
        <div className="min-w-0 flex-1">
          <Link
            href={`/platform-roadmap/${item.id}`}
            className="block font-medium rw-strong hover:underline"
          >
            {item.title}
          </Link>
          {item.body && (
            <p className="mt-1 text-theme-sm rw-dim">
              {excerpt(item.body, 120)}
            </p>
          )}
          <p className="mt-2 flex flex-wrap items-center gap-2 text-theme-xs rw-faint">
            {item.target_quarter && <span>{item.target_quarter}</span>}
            {item.comment_count > 0 && (
              // Shakl 10 tilda ham to'g'ri: son o'rin egallovchi ichida,
              // ya'ni ko'plik shaklini tanlash kerak emas.
              <span>
                {fill(t(locale, "roadmap.commentCount"), {
                  count: item.comment_count,
                })}
              </span>
            )}
          </p>
        </div>
      </div>
    </article>
  );
}

export default async function PlatformRoadmapPage() {
  const locale = await getLocale();

  // Mehmon ham o'qiydi; `mine` esa faqat kirganlarga (server tomonda
  // 401 bo'lsa `null` — brauzer konsoliga tushmaydi, bu SSR so'rovi).
  const [data, mine] = await Promise.all([
    api.roadmap(`?page_size=${BOARD_SIZE}`),
    getWithSession<RoadmapItem[]>("/platform-roadmap/mine/").catch(() => null),
  ]);

  const byStatus = new Map<RoadmapStatus, RoadmapItem[]>(
    ROADMAP_COLUMNS.map((status) => [status, []]),
  );
  const declined: RoadmapItem[] = [];
  for (const item of data.results) {
    const bucket = byStatus.get(item.status);
    if (bucket) bucket.push(item);
    else if (item.status === "declined") declined.push(item);
  }

  // `declined` ustun emas, lekin YASHIRILMAYDI: rad etilgan taklifni
  // ko'rsatish "yozdim, javob bo'lmadi" taassurotini yo'q qiladi.
  const hidden = data.count - data.results.length;

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <h1 className="text-title-sm font-bold rw-strong">
            {t(locale, "roadmap.title")}
          </h1>
          <p className="max-w-3xl text-theme-sm rw-dim">
            {t(locale, "roadmap.lead")}
          </p>
        </div>
        <RoadmapSuggest />
      </header>

      {hidden > 0 && (
        // JIMGINA kesish yo'q: kanban to'liq ko'rinmayotgani aytiladi.
        <p className="text-theme-sm rw-warn-ink">
          {fill(t(locale, "roadmap.truncated"), { count: hidden })}
        </p>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {ROADMAP_COLUMNS.map((status) => {
          const rows = byStatus.get(status) ?? [];
          return (
            <section key={status} className="space-y-3">
              <header className="flex items-center justify-between gap-2">
                <RoadmapStatusBadge status={status} locale={locale} />
                <span className="text-theme-xs tabular-nums rw-faint">
                  {rows.length}
                </span>
              </header>
              {rows.map((item) => (
                <RoadmapCard key={item.id} item={item} locale={locale} />
              ))}
              {rows.length === 0 && (
                <p className="rw-panel p-4 text-theme-sm rw-faint">
                  {t(locale, "roadmap.empty")}
                </p>
              )}
            </section>
          );
        })}
      </div>

      {declined.length > 0 && (
        <section className="space-y-3">
          <h2 className="flex items-center gap-2 text-theme-sm font-semibold rw-dim-2">
            {t(locale, "roadmap.declinedTitle")}
            <span className="text-theme-xs tabular-nums rw-faint">
              {declined.length}
            </span>
          </h2>
          <ul className="divide-y rw-divide rw-panel">
            {declined.map((item) => (
              <li key={item.id} className="px-5 py-3">
                <Link
                  href={`/platform-roadmap/${item.id}`}
                  className="flex flex-wrap items-center gap-2 text-theme-sm rw-dim-2 hover:underline"
                >
                  <RoadmapStatusBadge status={item.status} locale={locale} />
                  <span>{item.title}</span>
                  <span className="text-theme-xs rw-faint">
                    {date(item.created_at, locale)}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {mine && mine.length > 0 && (
        <Card title={t(locale, "roadmap.mine")} bodyClassName="p-0">
          <ul className="divide-y rw-divide">
            {mine.map((item) => (
              <li key={item.id}>
                <Link
                  href={`/platform-roadmap/${item.id}`}
                  className="flex flex-wrap items-center gap-2 px-5 py-4 transition rw-hover-bg"
                >
                  <RoadmapStatusBadge status={item.status} locale={locale} />
                  <span className="min-w-0 flex-1 truncate font-medium rw-strong">
                    {item.title}
                  </span>
                  <span className="text-theme-xs tabular-nums rw-faint">
                    {item.vote_count}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <p className="text-theme-sm rw-faint">
        <Link
          href={"/updates" as Route}
          className="font-medium rw-accent-ink hover:underline"
        >
          {t(locale, "update.back")}
        </Link>
      </p>
    </div>
  );
}
