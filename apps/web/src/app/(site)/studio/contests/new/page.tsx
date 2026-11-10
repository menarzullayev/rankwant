import type { Metadata } from "next";

import { ContestEditor, DEFAULT_CONTEST_TAB } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { requireUser } from "@/lib/access.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.contests.new"), robots: { index: false } };
}

export default async function StudioNewContestPage() {
  await requireUser("/studio/contests/new");
  return (
    <ContestEditor initial={null} drafts={[]} participants={[]} initialTab={DEFAULT_CONTEST_TAB} />
  );
}
