import type { Metadata } from "next";
import { Suspense } from "react";

import { OnboardingForm } from "@/features/account";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { requireUser } from "@/lib/access.server";
import type { Me } from "@/lib/api";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: t(await getLocale(), "auth.step2Title"),
    // Onboarding shaxsiy sahifa — qidiruvda kerak emas.
    robots: { index: false, follow: false },
  };
}

/** Ro'yxatdan o'tishning 2-qadami (qaror 3, 4).
 *
 * `AuthForm` ro'yxatdan keyin shu yerga yo'naltiradi. Kirilmagan bo'lsa
 * sahifaning ma'nosi yo'q — login'ga qaytaramiz.
 */
export default async function OnboardingPage() {
  // `?next=` bilan: kirgandan keyin odam AYNAN shu yerga qaytishi kerak,
  // aks holda 2-qadamni tugatib bosh sahifaga tushardi (qaror 1).
  const me = await requireUser<Me>("/onboarding");
  const locale = await getLocale();

  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold">
          Rank<span className="rw-accent-ink">Want</span>
        </h1>
      </div>
      <Card title={t(locale, "auth.step2Title")}>
        <Suspense>
          <OnboardingForm me={me} />
        </Suspense>
      </Card>
    </div>
  );
}
