import type { Metadata } from "next";

import { AuthForm } from "@/components/AuthForm";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "auth.login") };
}

export default async function LoginPage() {
  const locale = await getLocale();
  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <p className="text-2xl font-bold">
          Rank<span className="rw-accent-ink">Want</span>
        </p>
      </div>
      <Card title={t(locale, "auth.login")}>
        <AuthForm mode="login" />
      </Card>
    </div>
  );
}
