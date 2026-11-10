import type { Metadata } from "next";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

import { ProblemsAdmin } from "@/components/admin/ProblemsAdmin";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return { title: `${t(locale, "admin.title")} · ${t(locale, "admin.section.problems")}` };
}

type Props = { searchParams: Promise<{ review?: string }> };

/** `?review=1` opens the review queue — the link a review-request
 *  notification carries (`/studio`, 2026-11-10). */
export default async function AdminProblemsPage({ searchParams }: Props) {
  const { review } = await searchParams;
  return <ProblemsAdmin review={review === "1"} />;
}
