import type { Metadata } from "next";
import { Suspense } from "react";

import { AuthForm } from "@/components/AuthForm";
import { Card } from "@/components/ui/Card";
import { fetchProviders } from "@/lib/api";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "auth.login") };
}

export default async function LoginPage() {
  const [locale, auth] = await Promise.all([getLocale(), fetchProviders()]);
  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold">
          Rank<span className="rw-accent-ink">Want</span>
        </h1>
      </div>
      <Card title={t(locale, "auth.login")}>
        <Suspense>
          <AuthForm
            mode="login"
            providers={auth.providers}
            telegramBot={auth.telegram_bot}
          />
        </Suspense>
      </Card>
    </div>
  );
}
