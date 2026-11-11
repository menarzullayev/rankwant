import { dateKit } from "@rankwant/shared/format";
import type { Metadata, Route } from "next";
import Link from "next/link";

import { Card } from "@/components/ui/Card";
import { Icon } from "@/components/ui/Icon";
import { ActivityHeatmap } from "@/features/profile";
import { getLocale } from "@/i18n/server";
import { date, fill, t } from "@/i18n/messages";
import type { Calendar } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";

import { FreezeButton } from "./FreezeButton";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "streak.title"), robots: { index: false } };
}

type Streak = {
  current: number;
  longest: number;
  active_today: boolean;
  freeze_until: string | null;
  milestones: number[];
  freeze: { code: string; price: number } | null;
};

/** The reader's streak (decision 2026-11-11 ④): milestones 3 / 7 / 14 / 30 /
 *  100 / 365, a twelve-month calendar and the freeze from the shop. */
export default async function StreakPage() {
  const me = await requireUser("/streak");
  const locale = await getLocale();
  const [streak, calendar] = await Promise.all([
    getWithSession<Streak>("/qvant/streak/"),
    getWithSession<Calendar>(`/users/${encodeURIComponent(me.username)}/calendar/`),
  ]);
  const next = streak.milestones.find((m) => m > streak.current);

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">{t(locale, "streak.title")}</h1>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-5">
          <p className="text-theme-xs rw-faint">{t(locale, "streak.current")}</p>
          <p className="flex items-center gap-2 text-title-sm font-bold rw-strong">
            <Icon name="ranking.streak" className="size-7 rw-warn-ink" />
            {fill(t(locale, "streak.days"), { count: streak.current })}
          </p>
          <p className={`mt-1 text-theme-sm ${streak.active_today ? "rw-ok-ink" : "rw-warn-ink"}`}>
            {t(locale, streak.active_today ? "streak.todayDone" : "streak.todayOpen")}
          </p>
        </Card>
        <Card className="p-5">
          <p className="text-theme-xs rw-faint">{t(locale, "streak.longest")}</p>
          <p className="text-title-sm font-bold rw-strong">
            {fill(t(locale, "streak.days"), { count: streak.longest })}
          </p>
          {next !== undefined && (
            <p className="mt-1 text-theme-sm rw-dim">
              {fill(t(locale, "streak.next"), { milestone: next, left: next - streak.current })}
            </p>
          )}
        </Card>
        <Card className="space-y-2 p-5">
          <p className="text-theme-xs rw-faint">{t(locale, "streak.freeze")}</p>
          <p className="text-theme-sm rw-strong">
            {streak.freeze_until
              ? fill(t(locale, "streak.freezeUntil"), { date: date(streak.freeze_until, locale) })
              : t(locale, "streak.freezeNone")}
          </p>
          <p className="text-theme-xs rw-dim">{t(locale, "streak.freezeHint")}</p>
          {streak.freeze && <FreezeButton code={streak.freeze.code} price={streak.freeze.price} />}
        </Card>
      </div>

      <Card title={t(locale, "streak.milestones")}>
        <ol className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {streak.milestones.map((milestone) => {
            const reached = streak.longest >= milestone;
            const progress = Math.min(100, Math.round((streak.current / milestone) * 100));
            return (
              <li
                key={milestone}
                className={`space-y-2 rw-radius-sm border p-3 ${reached ? "rw-accent-line" : "rw-line"}`}
              >
                <p className="flex items-center justify-between gap-2 text-theme-sm font-semibold rw-strong">
                  {fill(t(locale, "streak.days"), { count: milestone })}
                  {reached && <span className="rw-ok-ink">✓</span>}
                </p>
                <span className="block h-2 overflow-hidden rounded-full rw-chip" aria-hidden="true">
                  <span className="block h-full rounded-full rw-accent-bg" style={{ width: `${progress}%` }} />
                </span>
                <p className="text-theme-xs rw-faint">
                  {reached
                    ? t(locale, "streak.reached")
                    : fill(t(locale, "streak.progress"), { count: streak.current, milestone })}
                </p>
              </li>
            );
          })}
        </ol>
      </Card>

      <Card title={t(locale, "streak.calendar")} bodyClassName="space-y-3">
        <ActivityHeatmap username={me.username} initial={calendar} kit={dateKit(locale)} />
        <Link href={"/qvant" as Route} className="text-theme-sm rw-accent-ink rw-link-hover">
          {t(locale, "streak.shop")}
        </Link>
      </Card>
    </div>
  );
}
