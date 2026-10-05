import type { Metadata } from "next";
import type { Route } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { SettingsShell } from "@/features/account";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";
import type { Me } from "@/lib/api";
import { getSessionUser } from "@/lib/api.server";

type Props = { searchParams: Promise<{ social?: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "settings.title"), robots: { index: false } };
}

/** The settings index: on a phone the list of sections, on a wide screen
 *  the list beside the first one.
 *
 *  It used to redirect to the first section. A phone then never saw the
 *  list as a screen of its own — it got a select above every section.
 *
 *  `/settings?social=…` is the provider coming back from linking a sign-in
 *  method; that lives under Security now. */
export default async function SettingsPage({ searchParams }: Props) {
  const { social } = await searchParams;
  if (social) {
    redirect(`/settings/xavfsizlik?social=${encodeURIComponent(social)}` as Route);
  }
  const me = await getSessionUser<Me>();
  if (!me) redirect(`/login?next=${encodeURIComponent("/settings")}`);

  return (
    <Suspense>
      <SettingsShell section={null} tab="" />
    </Suspense>
  );
}
