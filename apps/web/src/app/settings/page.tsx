import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AccountSettings } from "@/components/AccountSettings";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { UserPublic } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: t(await getLocale(), "settings.title"),
    robots: { index: false },
  };
}

export const dynamic = "force-dynamic";

export default async function SettingsPage() {
  const locale = await getLocale();
  // Sahifa faqat o'z hisobi haqida — kirmagan foydalanuvchiga
  // ko'rsatiladigan hech narsasi yo'q.
  const me = await getWithSession<UserPublic>("/me/").catch(() => null);
  if (!me) redirect("/login");

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "settings.title")}
      </h1>
      <AccountSettings />
    </div>
  );
}
