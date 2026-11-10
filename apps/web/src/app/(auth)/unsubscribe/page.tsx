import type { Metadata } from "next";
import { Suspense } from "react";

import { EmailUnsubscribe } from "@/features/account";
import { AuthShell } from "@/features/auth/server";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: t(await getLocale(), "unsubscribe.title"),
    // The link carries a signed token: it must not reach a search engine.
    robots: { index: false, follow: false },
  };
}

/** Switch notification email off from a mail (2026-11-10). Opened from an
 *  inbox, often on another device: no sign-in, and the same chrome-less
 *  shell as the address confirmation page. */
export default async function UnsubscribePage() {
  const locale = await getLocale();
  return (
    <AuthShell>
      <h1 className="mb-5 text-2xl font-bold rw-strong">{t(locale, "unsubscribe.title")}</h1>
      <Suspense>
        <EmailUnsubscribe />
      </Suspense>
    </AuthShell>
  );
}
