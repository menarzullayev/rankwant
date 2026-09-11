import type { Metadata } from "next";

import { ContestsTab } from "@/components/profile/ContestsTab";
import { getLocale } from "@/i18n/server";
import { tabMetadata } from "@/lib/profile.server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export function generateMetadata({ params }: Props): Promise<Metadata> {
  return tabMetadata(params, "profile.tab.contests");
}

export default async function Page({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const { q, page } = await searchParams;
  return <ContestsTab username={username} query={{ q, page }} locale={locale} />;
}
