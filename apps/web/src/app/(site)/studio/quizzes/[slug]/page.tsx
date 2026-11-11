import type { Metadata } from "next";

import { QuizEditor } from "@/features/studio";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { requireUser } from "@/lib/access.server";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "studio.nav.quizzes"), robots: { index: false } };
}

export default async function Page({ params }: Props) {
  const { slug } = await params;
  await requireUser(`/studio/quizzes/${slug}`);
  return <QuizEditor slug={slug} />;
}
