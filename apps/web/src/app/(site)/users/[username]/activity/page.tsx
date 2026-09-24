import type { Metadata } from "next";

import { ActivityTab } from "@/features/profile/server";
import { getLocale } from "@/i18n/server";
import { tabMetadata } from "@/lib/profile.server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export function generateMetadata({ params }: Props): Promise<Metadata> {
  return tabMetadata(params, "profile.tab.activity");
}

export default async function Page({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const { before } = await searchParams;
  return <ActivityTab username={username} before={before} locale={locale} />;
}
