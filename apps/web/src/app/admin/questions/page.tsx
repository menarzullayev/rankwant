import type { Metadata } from "next";

import { QuestionsAdmin } from "@/components/admin/QuestionsAdmin";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin · Savol banki" };

export default function AdminQuestionsPage() {
  return <QuestionsAdmin />;
}
