import type { Metadata } from "next";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

import { ArenaAdmin } from "@/components/admin/ArenaAdmin";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return { title: `${t(locale, "admin.title")} · ${t(locale, "admin.section.arena")}` };
}

export default function AdminArenaPage() {
  return <ArenaAdmin />;
}
