import type { Metadata } from "next";
import { Suspense } from "react";

import { EmailVerify } from "@/features/account";
import { AuthShell } from "@/features/auth/server";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: t(await getLocale(), "auth.verifyTitle"),
    // A link with a token must not reach a search engine — same reason as
    // the reset page.
    robots: { index: false, follow: false },
  };
}

/** Confirm the e-mail, drawn in the same two-column shell as the sign-in
 *  page (2026-10-26): a person arrives here from the sign-up and should not
 *  find the site's header and footer in the middle of it. */
export default async function VerifyPage() {
  const locale = await getLocale();
  return (
    <AuthShell>
      <h1 className="mb-5 text-2xl font-bold rw-strong">{t(locale, "auth.verifyTitle")}</h1>
      <Suspense>
        <EmailVerify />
      </Suspense>
    </AuthShell>
  );
}
