import type { Metadata } from "next";

import { AboutTab } from "@/components/profile/AboutTab";
import { loadProfile } from "@/lib/profile.server";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = { params: Promise<{ username: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "profile.tab.about") };
}

export default async function Page({ params }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const profile = await loadProfile(username);
  return <AboutTab profile={profile} locale={locale} />;
}
