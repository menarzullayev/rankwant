import type { Metadata } from "next";

import { AttemptsTab } from "@/features/profile";
import { getLocale } from "@/i18n/server";
import { tabMetadata } from "@/lib/profile.server";

type Props = {
  params: Promise<{ username: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
};

export const dynamic = "force-dynamic";

export function generateMetadata({ params }: Props): Promise<Metadata> {
  return tabMetadata(params, "profile.tab.attempts");
}

export default async function Page({ params, searchParams }: Props) {
  const username = decodeURIComponent((await params).username);
  const locale = await getLocale();
  const { problem, verdict, language, cursor } = await searchParams;
  return (
    <AttemptsTab
      username={username}
      filters={{ problem, verdict, language, cursor }}
      locale={locale}
    />
  );
}
