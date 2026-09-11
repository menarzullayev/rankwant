import type { Metadata } from "next";

import { ContestsTab } from "@/components/profile/ContestsTab";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "profile.tab.contests") };
}

export default async function Page({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const { q, page } = await searchParams;
  return <ContestsTab username={username} query={{ q, page }} locale={locale} />;
}
