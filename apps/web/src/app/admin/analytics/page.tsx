import type { Metadata } from "next";

import { AnalyticsDashboard } from "@/components/admin/AnalyticsDashboard";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Analitika" };

/** Voronka dashboardi (qaror 7).
 *
 *  Sahifaning o'zi faqat qobiq: ma'lumot client komponentda olinadi,
 *  chunki oyna (7/30/90 kun) almashganda qayta so'rov ketadi va butun
 *  sahifani qayta chizishning ma'nosi yo'q.
 */
export default function AdminAnalyticsPage() {
  return <AnalyticsDashboard />;
}
