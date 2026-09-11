import type { Metadata } from "next";

import { AchievementsTab } from "@/components/profile/ActivityTabs";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = { params: Promise<{ username: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "profile.tab.achievements") };
}

export default async function Page({ params }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  return <AchievementsTab username={username} locale={locale} />;
}
