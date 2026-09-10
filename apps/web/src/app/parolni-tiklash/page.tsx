import type { Metadata } from "next";
import { Suspense } from "react";

import { ResetForm } from "@/components/ResetForm";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: t(await getLocale(), "reset.title"),
    // Tiklash sahifasi qidiruvda kerak emas va tokenli havola
    // indekslanmasligi kerak.
    robots: { index: false, follow: false },
  };
}

export default async function ResetPage() {
  const locale = await getLocale();
  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold">
          Rank<span className="rw-accent-ink">Want</span>
        </h1>
      </div>
      <Card title={t(locale, "reset.title")}>
        <Suspense>
          <ResetForm />
        </Suspense>
      </Card>
    </div>
  );
}
