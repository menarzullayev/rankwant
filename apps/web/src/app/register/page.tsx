import type { Metadata } from "next";
import { Suspense } from "react";

import { AuthForm } from "@/components/AuthForm";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "auth.register") };
}

export default async function RegisterPage() {
  const locale = await getLocale();
  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold">
          Rank<span className="rw-accent-ink">Want</span>
        </h1>
      </div>
      <Card title={t(locale, "auth.register")}>
        <Suspense>
          <AuthForm mode="register" />
        </Suspense>
      </Card>
    </div>
  );
}
