import type { Metadata } from "next";

import { ContestList, type MineContest } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { Paginated } from "@/lib/api";
import { requireUser } from "@/lib/access.server";
import { getWithSession } from "@/lib/api.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.nav.contests"), robots: { index: false } };
}

export default async function StudioContestsPage() {
  await requireUser("/studio/contests");
  const locale = await getLocale();
  const page = await getWithSession<Paginated<MineContest>>("/contests/mine/?page_size=100");
  return <ContestList rows={page.results} locale={locale} />;
}
