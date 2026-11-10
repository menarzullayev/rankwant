import type { Metadata } from "next";

import { DEFAULT_TAB, ProblemEditor } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { requireUser } from "@/lib/access.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.problems.new"), robots: { index: false } };
}

export default async function StudioNewProblemPage() {
  await requireUser("/studio/problems/new");
  return <ProblemEditor initial={null} initialTests={[]} initialTab={DEFAULT_TAB} />;
}
