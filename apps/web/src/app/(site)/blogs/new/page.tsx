import type { Metadata } from "next";

import { SignInGate } from "@/components/auth/SignInGate";
import { Card } from "@/components/ui/Card";
import { EntryEditor } from "@/features/community";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { getSessionUser } from "@/lib/api.server";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "blogs.newTitle"), robots: { index: false } };
}

/** Anyone signed in writes (decision ④); a guest gets the sign-in card. */
export default async function NewEntryPage() {
  const locale = await getLocale();
  const signedIn = (await getSessionUser()) !== null;
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">{t(locale, "blogs.newTitle")}</h1>
      {signedIn ? (
        <Card className="p-5">
          <EntryEditor />
        </Card>
      ) : (
        <SignInGate reason="blog" />
      )}
    </div>
  );
}
