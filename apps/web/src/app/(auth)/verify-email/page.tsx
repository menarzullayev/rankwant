import type { Metadata } from "next";
import { Suspense } from "react";

import { EmailVerify } from "@/features/account";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: t(await getLocale(), "auth.verifyTitle"),
    // Tokenli havola qidiruvga tushmasligi kerak — tiklash sahifasidagi
    // bilan bir xil sabab.
    robots: { index: false, follow: false },
  };
}

export default async function VerifyPage() {
  const locale = await getLocale();
  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold">
          Rank<span className="rw-accent-ink">Want</span>
        </h1>
      </div>
      <Card title={t(locale, "auth.verifyTitle")}>
        <Suspense>
          <EmailVerify />
        </Suspense>
      </Card>
    </div>
  );
}
