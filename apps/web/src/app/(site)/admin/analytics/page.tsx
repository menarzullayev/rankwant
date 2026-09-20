import type { Metadata } from "next";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

import { AnalyticsDashboard } from "@/components/admin/AnalyticsDashboard";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return { title: `${t(locale, "admin.title")} · ${t(locale, "admin.section.analytics")}` };
}

/** Voronka dashboardi (qaror 7).
 *
 *  Sahifaning o'zi faqat qobiq: ma'lumot client komponentda olinadi,
 *  chunki oyna (7/30/90 kun) almashganda qayta so'rov ketadi va butun
 *  sahifani qayta chizishning ma'nosi yo'q.
 */
export default function AdminAnalyticsPage() {
  return <AnalyticsDashboard />;
}
