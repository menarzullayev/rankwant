import type { Metadata } from "next";

import { AuthForm } from "@/components/AuthForm";
import { Card } from "@/components/ui/Card";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: t(DEFAULT_LOCALE, "auth.register") };

export default function RegisterPage() {
  return (
    <div className="mx-auto max-w-md py-10">
      <div className="mb-6 text-center">
        <p className="text-2xl font-bold">
          Rank<span className="text-brand-500">Want</span>
        </p>
      </div>
      <Card title={t(DEFAULT_LOCALE, "auth.register")}>
        <AuthForm mode="register" />
      </Card>
    </div>
  );
}
