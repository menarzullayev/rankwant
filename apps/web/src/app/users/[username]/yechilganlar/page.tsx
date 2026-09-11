import type { Metadata } from "next";

import { SolvedTab } from "@/components/profile/SolvedTab";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "profile.tab.solved") };
}

export default async function Page({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const { view, q, ordering, page } = await searchParams;
  return <SolvedTab username={username} query={{ view, q, ordering, page }} locale={locale} />;
}
