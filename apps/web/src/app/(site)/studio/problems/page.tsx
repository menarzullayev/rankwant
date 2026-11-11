import type { Metadata } from "next";

import { ProblemList, type MineProblem } from "@/features/studio";
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
  return { title: t(await getLocale(), "studio.nav.problems"), robots: { index: false } };
}

export default async function StudioProblemsPage() {
  await requireUser("/studio/problems");
  const locale = await getLocale();
  // The newest hundred: the free plan holds 20 problems in all.
  const [page, quotas] = await Promise.all([
    getWithSession<Paginated<MineProblem>>("/problems/mine/?page_size=100"),
    readQuotas(),
  ]);
  return <ProblemList rows={page.results} quota={quotaOf(quotas, "problems")} locale={locale} />;
}
