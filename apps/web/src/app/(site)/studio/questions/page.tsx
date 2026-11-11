import type { Metadata } from "next";

import { QuestionBank } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { requireUser } from "@/lib/access.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.nav.questions"), robots: { index: false } };
}

export default async function Page() {
  await requireUser("/studio/questions");
  return <QuestionBank />;
}
