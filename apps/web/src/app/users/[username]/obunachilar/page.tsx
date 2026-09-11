import type { Metadata } from "next";

import { PeopleTab } from "@/components/profile/ActivityTabs";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "profile.followers") };
}

export default async function Page({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const { page } = await searchParams;
  return (
    <PeopleTab
      username={username}
      direction="followers"
      page={Math.max(1, Number(page) || 1)}
      locale={locale}
    />
  );
}
