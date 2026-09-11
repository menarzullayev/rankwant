import type { Metadata } from "next";

import { AboutTab } from "@/components/profile/AboutTab";
import { loadProfile, tabMetadata } from "@/lib/profile.server";
import { getLocale } from "@/i18n/server";

type Props = { params: Promise<{ username: string }> };

export const dynamic = "force-dynamic";

export function generateMetadata({ params }: Props): Promise<Metadata> {
  return tabMetadata(params, "profile.tab.about");
}

export default async function Page({ params }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const profile = await loadProfile(username);
  return <AboutTab profile={profile} locale={locale} />;
}
