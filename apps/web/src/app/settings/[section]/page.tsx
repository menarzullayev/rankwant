import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { Suspense } from "react";

import { SettingsShell } from "@/components/settings/SettingsShell";
import { SECTIONS, isSection } from "@/components/settings/sections";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { Me } from "@/lib/api";
import { getSessionUser } from "@/lib/api.server";

type Props = { params: Promise<{ section: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { section } = await params;
  const locale = await getLocale();
  const current = SECTIONS.find((s) => s.id === section);
  const title = t(locale, "settings.title");
  return {
    title: current ? `${t(locale, current.key)} · ${title}` : title,
    robots: { index: false },
  };
}

export default async function SettingsSectionPage({ params }: Props) {
  const { section } = await params;
  if (!isSection(section)) notFound();
  // Sahifa faqat o'z hisobi haqida — kirmagan foydalanuvchiga
  // ko'rsatiladigan hech narsasi yo'q. `?next=` bilan qaytariladi:
  // sozlamaga kirish uchun kirgan odam o'sha bo'limga qaytishi kerak,
  // bosh sahifaga emas (qaror 1).
  const me = await getSessionUser<Me>();
  if (!me) redirect(`/login?next=${encodeURIComponent(`/settings/${section}`)}`);

  return (
    <Suspense>
      <SettingsShell section={section} />
    </Suspense>
  );
}
