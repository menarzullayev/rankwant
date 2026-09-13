import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { AuthForm } from "@/components/AuthForm";
import { AuthLayout } from "@/components/AuthLayout";
import { Card } from "@/components/ui/Card";
import { fetchProviders } from "@/lib/api";
import { isSignedIn } from "@/lib/server-session";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "auth.login") };
}

export default async function LoginPage() {
  // Kirgan odamga bo'sh forma ko'rsatishning ma'nosi yo'q.
  if (await isSignedIn()) redirect("/");

  const [locale, auth] = await Promise.all([getLocale(), fetchProviders()]);
  return (
    <AuthLayout>
      <Card title={t(locale, "auth.login")}>
        <Suspense>
          <AuthForm mode="login" providers={auth.providers} />
        </Suspense>
      </Card>
    </AuthLayout>
  );
}
