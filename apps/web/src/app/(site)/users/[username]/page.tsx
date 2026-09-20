import type { Route } from "next";
import { redirect } from "next/navigation";

import { ActivityHeatmap } from "@/components/profile/ActivityHeatmap";
import { LanguageCards } from "@/components/profile/LanguageCards";
import { ProblemMap } from "@/components/profile/ProblemMap";
import { RatingChart } from "@/components/profile/RatingChart";
import { RatingHistoryTable } from "@/components/profile/RatingHistoryTable";
import { SectionHint } from "@/components/profile/SectionHint";
import { SolvedOverview } from "@/components/profile/SolvedOverview";
import { TopicStrength } from "@/components/profile/TopicStrength";
import { Card } from "@/components/ui/Card";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { api, type Calendar, type ProblemTile } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";
import { dateKit } from "@/lib/format";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<{ tab?: string }>;
};

export const dynamic = "force-dynamic";

/** Eski `?tab=` havolalari (ulashilgan bo'lishi mumkin) yangi manzilga.
 *
 *  Boshqa kalitlar (`activity`, `achievements`, `purchases`, `followers`,
 *  `following`) endi slug bilan AYNAN bir xil, ya'ni yo'naltirish kerak
 *  emas — ular 2026-09-13 gacha `shaxsiy`/`faoliyat`/… bo'lgan, endi
 *  inglizcha asl nomiga qaytdi. Faqat `about` mos kelmaydi. */
const LEGACY: Record<string, string> = {
  about: "profile",
};

export default async function ProfileOverviewPage({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const { tab } = await searchParams;
  if (tab && LEGACY[tab]) redirect(`/users/${username}/${LEGACY[tab]}` as Route);
  const locale = await getLocale();
  const kit = dateKit(locale);

  const [stats, series, calendar, map, topics, history] = await Promise.all([
    api.userStats(username),
    api.ratingSeries(username),
    getWithSession<Calendar>(`/users/${username}/calendar/`),
    getWithSession<{ problems: ProblemTile[]; hidden?: boolean }>(
      `/users/${username}/problem-map/`,
    ),
    api.userTopics(username),
    api.ratingHistory(username),
  ]);

  return (
    <div className="space-y-6">
      <SolvedOverview stats={stats} locale={locale} />

      <Card title={t(locale, "profile.history")} bodyClassName="space-y-4">
        <SectionHint>{t(locale, "profile.ratingHint")}</SectionHint>
        <RatingChart data={series} kit={kit} />
        <RatingHistoryTable rows={history.results} locale={locale} />
      </Card>

      <Card title={t(locale, "profile.heatmapTitle")} bodyClassName="space-y-4">
        {calendar.hidden ? (
          <p className="text-theme-sm rw-dim">{t(locale, "profile.heatmapHidden")}</p>
        ) : (
          <>
            <SectionHint>{t(locale, "profile.heatmapHint")}</SectionHint>
            <ActivityHeatmap username={username} initial={calendar} kit={kit} />
          </>
        )}
      </Card>

      <Card title={t(locale, "profile.mapTitle")} bodyClassName="space-y-4">
        {map.hidden ? (
          <p className="text-theme-sm rw-dim">{t(locale, "profile.mapHidden")}</p>
        ) : (
          <>
            <SectionHint>{t(locale, "profile.mapHint")}</SectionHint>
            <ProblemMap username={username} problems={map.problems} />
          </>
        )}
      </Card>

      <div className="grid gap-6 xl:grid-cols-2">
        <LanguageCards languages={stats.languages} locale={locale} />
        <TopicStrength topics={topics.topics} locale={locale} />
      </div>
    </div>
  );
}
