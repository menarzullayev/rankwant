import type { Metadata } from "next";
import { Suspense } from "react";

import { OnboardingForm } from "@/features/account";
import { AuthShell } from "@/features/auth/server";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { requireUser } from "@/lib/access.server";
import type { Me } from "@/lib/api";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: t(await getLocale(), "auth.step2Title"),
    // A personal page — not for a search engine.
    robots: { index: false, follow: false },
  };
}

/** The second half of sign-up, in the same two-column shell as the sign-in
 *  page (2026-10-26): three short optional steps, no site header or footer.
 *
 *  `AuthForm` sends the person here after the sign-up; someone who is not
 *  signed in is sent to the sign-in page, with a way back. */
export default async function OnboardingPage() {
  // With `?next=`: after signing in the person must land HERE again, or they
  // would finish at the home page without ever seeing the steps.
  const me = await requireUser<Me>("/onboarding");

  return (
    <AuthShell>
      <Suspense>
        <OnboardingForm me={me} />
      </Suspense>
    </AuthShell>
  );
}
