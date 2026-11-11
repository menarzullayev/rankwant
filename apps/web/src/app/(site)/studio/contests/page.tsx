import type { Metadata } from "next";

import { ContestList, type MineContest } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { Paginated } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";
import { quotaOf, type Quotas } from "@/lib/quotas";

export const dynamic = "force-dynamic";

/** The plan's limit; a failed read leaves the button to the server's refusal. */
async function readQuotas(): Promise<Quotas | null> {
  try {
    return await getWithSession<Quotas>("/me/quotas/");
  } catch {
    return null;
  }
}

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.nav.contests"), robots: { index: false } };
}

export default async function StudioContestsPage() {
  await requireUser("/studio/contests");
  const locale = await getLocale();
  const [page, quotas] = await Promise.all([
    getWithSession<Paginated<MineContest>>("/contests/mine/?page_size=100"),
    readQuotas(),
  ]);
  return <ContestList rows={page.results} quota={quotaOf(quotas, "contests")} locale={locale} />;
}
