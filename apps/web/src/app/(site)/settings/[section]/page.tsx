import type { Metadata } from "next";
import type { Route } from "next";
import { notFound, redirect } from "next/navigation";
import { Suspense } from "react";

import { SECTIONS, SettingsShell, isSection, legacyTarget, tabOf } from "@/features/account";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import { requireUser } from "@/lib/access.server";

type Query = Record<string, string | string[] | undefined>;
type Props = { params: Promise<{ section: string }>; searchParams: Promise<Query> };

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

/** The first value of each query key — a repeated key is not something
 *  these pages use. */
function flat(query: Query): Record<string, string | undefined> {
  return Object.fromEntries(
    Object.entries(query).map(([key, value]) => [key, Array.isArray(value) ? value[0] : value]),
  );
}

export default async function SettingsSectionPage({ params, searchParams }: Props) {
  const { section } = await params;
  const query = flat(await searchParams);
  // An address from the ten-section layout: bookmarks, team invite links
  // already sent, the provider's return URL.
  const moved = legacyTarget(section, query);
  if (moved) redirect(moved as Route);
  if (!isSection(section)) notFound();
  // Sahifa faqat o'z hisobi haqida — kirmagan foydalanuvchiga
  // ko'rsatiladigan hech narsasi yo'q. `?next=` bilan qaytariladi:
  // sozlamaga kirish uchun kirgan odam o'sha bo'limga qaytishi kerak,
  // bosh sahifaga emas (qaror 1).
  await requireUser(`/settings/${section}`);

  return (
    <Suspense>
      <SettingsShell section={section} tab={tabOf(section, query.tab)} />
    </Suspense>
  );
}
