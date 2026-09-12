import type { Metadata } from "next";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { AuthForm } from "@/components/AuthForm";
import { AuthLayout } from "@/components/AuthLayout";
import { Card } from "@/components/ui/Card";
import { fetchProviders } from "@/lib/api";
import { EXP_COOKIE, GEO_EXPERIMENT, parseVariants } from "@/lib/experiments";
import { isSignedIn } from "@/lib/server-session";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "auth.register") };
}

export default async function RegisterPage() {
  // Kirgan odamga bo'sh forma ko'rsatishning ma'nosi yo'q.
  if (await isSignedIn()) redirect("/");

  const [locale, auth] = await Promise.all([getLocale(), fetchProviders()]);
  // A/B guruhi SERVERDA o'qiladi (8-qaror). Mijozda o'qilsa server `a`,
  // mijoz `b` chizib hidratsiya mos kelmasligi mumkin edi — viloyat
  // maydoni paydo bo'lib, sahifa sakrardi.
  const geoVariant = parseVariants(
    (await cookies()).get(EXP_COOKIE)?.value,
    GEO_EXPERIMENT,
  );
  return (
    <AuthLayout>
      <Card title={t(locale, "auth.register")}>
        <Suspense>
          <AuthForm
            mode="register"
            providers={auth.providers}
            telegramBot={auth.telegram_bot}
            geoVariant={geoVariant}
          />
        </Suspense>
      </Card>
    </AuthLayout>
  );
}
