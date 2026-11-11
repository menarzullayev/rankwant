import type { Metadata } from "next";

import { CoachingPage } from "@/features/coaching";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { requireUser } from "@/lib/access.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "coaching.title"), robots: { index: false } };
}

export default async function CoachingRoute() {
  await requireUser("/coaching");
  return <CoachingPage />;
}
