import type { Metadata } from "next";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

import { TutorAdmin } from "@/components/admin/TutorAdmin";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return { title: `${t(locale, "admin.title")} · ${t(locale, "admin.section.tutor")}` };
}

/** AI tutor (ADR-0065): the monthly budget and the reported replies.
 *  The data is read in the client component, like the email quota page. */
export default function AdminTutorPage() {
  return <TutorAdmin />;
}
