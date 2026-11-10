import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { langQuery } from "@/features/courses";
import { PlanCards, type BillingOverview } from "@/features/billing";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { getSessionUser, getWithSession } from "@/lib/api.server";
import { isOnServer } from "@/lib/flags";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  if (!isOnServer("billing", undefined)) return { title: "404" };
  const locale = await getLocale();
  return { title: t(locale, "billing.title"), description: t(locale, "billing.intro") };
}

/** Plans on sale (ADR-0057). Behind the `billing` flag until the merchant
 *  accounts and the offer are ready. */
export default async function PlansPage() {
  if (!isOnServer("billing", undefined)) notFound();
  const locale = await getLocale();
  const lang = langQuery(locale);
  const [overview, me] = await Promise.all([
    getWithSession<BillingOverview>(`/billing/plans/${lang ? `?${lang}` : ""}`),
    getSessionUser<{ username: string }>(),
  ]);
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "billing.title")}</h1>
        <p className="max-w-2xl text-theme-sm rw-dim">{t(locale, "billing.intro")}</p>
      </header>
      <PlanCards overview={overview} signedIn={me !== null} />
    </div>
  );
}
