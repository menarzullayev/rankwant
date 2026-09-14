import type { Metadata } from "next";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

import { QuestionsAdmin } from "@/components/admin/QuestionsAdmin";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return { title: `${t(locale, "admin.title")} · ${t(locale, "admin.section.questions")}` };
}

export default function AdminQuestionsPage() {
  return <QuestionsAdmin />;
}
