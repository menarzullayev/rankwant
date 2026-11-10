import type { Metadata } from "next";

import { ProblemList, type MineProblem } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { Paginated } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.nav.problems"), robots: { index: false } };
}

export default async function StudioProblemsPage() {
  await requireUser("/studio/problems");
  const locale = await getLocale();
  // One page holds every draft: an author has at most 20 unpublished
  // problems (`MAX_DRAFTS`), well inside the API's page of 25.
  const page = await getWithSession<Paginated<MineProblem>>("/problems/mine/?page_size=100");
  return <ProblemList rows={page.results} locale={locale} />;
}
