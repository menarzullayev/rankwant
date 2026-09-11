import type { Metadata } from "next";

import { PurchasesTab } from "@/components/profile/ActivityTabs";
import { getLocale } from "@/i18n/server";
import { tabMetadata } from "@/lib/profile.server";

type Props = { params: Promise<{ username: string }> };

export const dynamic = "force-dynamic";

export function generateMetadata({ params }: Props): Promise<Metadata> {
  return tabMetadata(params, "profile.tab.purchases");
}

export default async function Page({ params }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  return <PurchasesTab username={username} locale={locale} />;
}
