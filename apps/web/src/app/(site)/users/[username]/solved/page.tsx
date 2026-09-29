import type { Metadata } from "next";

import { SolvedTab } from "@/features/profile";
import { getLocale } from "@/i18n/server";
import { tabMetadata } from "@/lib/profile.server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export function generateMetadata({ params }: Props): Promise<Metadata> {
  return tabMetadata(params, "profile.tab.solved");
}

export default async function Page({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const { view, q, ordering, page } = await searchParams;
  return <SolvedTab username={username} query={{ view, q, ordering, page }} locale={locale} />;
}
