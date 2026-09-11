import type { Metadata } from "next";

import { PeopleTab } from "@/components/profile/ActivityTabs";
import { getLocale } from "@/i18n/server";
import { tabMetadata } from "@/lib/profile.server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export function generateMetadata({ params }: Props): Promise<Metadata> {
  return tabMetadata(params, "profile.followers");
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
