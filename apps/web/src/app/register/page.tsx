import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { AuthForm } from "@/components/AuthForm";
import { Card } from "@/components/ui/Card";
import { fetchProviders } from "@/lib/api";
import { isSignedIn } from "@/lib/server-session";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "auth.register") };
}

export default async function RegisterPage() {
  // Kirgan odamga bo'sh forma ko'rsatishning ma'nosi yo'q.
  if (await isSignedIn()) redirect("/");

  const [locale, auth] = await Promise.all([getLocale(), fetchProviders()]);
  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold">
          Rank<span className="rw-accent-ink">Want</span>
        </h1>
      </div>
      <Card title={t(locale, "auth.register")}>
        <Suspense>
          <AuthForm
            mode="register"
            providers={auth.providers}
            telegramBot={auth.telegram_bot}
          />
        </Suspense>
      </Card>
    </div>
  );
}
