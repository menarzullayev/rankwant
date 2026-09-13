import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { AuthForm } from "@/components/AuthForm";
import { AuthFormSkeleton } from "@/components/AuthFormSkeleton";
import { AuthProof } from "@/components/auth/AuthProof";
import { AuthShell } from "@/components/auth/AuthShell";
import { AuthTabs } from "@/components/auth/AuthTabs";
import { ResetForm } from "@/components/ResetForm";
import { Card } from "@/components/ui/Card";
import { fetchProviders } from "@/lib/api";
import { parseTab, DEFAULT_TAB, type TabId } from "@/lib/auth-tabs";
import { isSignedIn } from "@/lib/server-session";
import { safeNext } from "@/lib/site";
import { getLocale } from "@/i18n/server";
import { t, type MessageKey } from "@/i18n/messages";

/** Bo'lim → karta sarlavhasi.
 *
 *  Kirishda sarlavha YO'Q (`null`): forma qisqa va maydonlar o'zi nima
 *  ekanini aytadi, sarlavha esa «Kirish» bo'lib tugma matnini
 *  takrorlardi. Ro'yxatda sarlavha «Hisob yaratish» — u QILINAYOTGAN
 *  ishni aytadi, tugma esa amalni, ya'ni takror yo'q. */
const TITLE: Record<TabId, MessageKey | null> = {
  login: null,
  register: "auth.createAccount",
  "reset-password": "reset.title",
};

type Query = Record<string, string | string[] | undefined>;

/** Manzil qatoridan bo'limni o'qiydi. `searchParams` — Promise, ya'ni
 *  uni HAR chaqiruvda qayta kutish mumkin emas (Next tagida bir marta
 *  o'qiladigan obyekt beradi) — shuning uchun bir marta kutib,
 *  natijani uzatamiz. */
function tabOf(params: Query): TabId {
  return parseTab(one(params.tab)) ?? DEFAULT_TAB;
}

/** Query qiymati bitta satr bo'lsa shuni, massiv bo'lsa BIRINCHISINI
 *  qaytaradi. `?next=a&next=b` — buzuq kiritish, ya'ni birinchisini
 *  olish kifoya; `string[]` ni to'g'ridan-to'g'ri uzatish tip xatosi
 *  beradi va `String([...])` esa `"a,b"` yasab qo'yardi. */
function one(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function nextOf(params: Query): string | undefined {
  return one(params.next);
}

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<Query>;
}): Promise<Metadata> {
  const params = await searchParams;
  const [locale, tab] = [await getLocale(), tabOf(params)];
  const title = TITLE[tab];
  return {
    title: t(locale, title ?? "auth.login"),
    //: Tiklash bo'limida tokenli havola bo'lishi mumkin — qidiruvda
    //: kerak emas. Kirish va ro'yxat esa indekslanadi (SEO).
    robots: tab === "reset-password" ? { index: false, follow: false } : undefined,
  };
}

/** Uch bo'lim, bitta markazlashgan karta (1 va 18-qarorlar).
 *
 *  Ildiz manzil — `/kirish`. `?tab=` bo'lmasa kirish ochiladi, ya'ni
 *  `/kirish` ni yoddan yozgan odam ham to'g'ri joyga tushadi. */
export default async function AuthPage({
  searchParams,
}: {
  searchParams: Promise<Query>;
}) {
  const params = await searchParams;
  const tab = tabOf(params);

  //: Kirgan odamga bo'sh forma ko'rsatishning ma'nosi yo'q. `next`
  //: qaytariladi, lekin faqat ICHKI yo'l: `safeNext` ochiq redirectni
  //: to'sadi (`//evil.com`, `/\evil.com`).
  if (await isSignedIn()) redirect((safeNext(nextOf(params)) ?? "/") as never);

  const [locale, auth] = await Promise.all([getLocale(), fetchProviders()]);
  const title = TITLE[tab];

  return (
    <AuthShell>
      <Card title={title ? t(locale, title) : undefined}>
        {/* Skeleton ham bo'lim tugmalari ostida turadi: aks holda karta
            ikki marta sakrab ko'rinardi (avval tugmalar, keyin forma).
            `AuthTabs` ichida `useSearchParams` bor, ya'ni `Suspense`
            SHART — usiz butun marshrut dinamik bo'lib qolardi. */}
        <Suspense fallback={<AuthFormSkeleton />}>
          <AuthTabs active={tab} />
          {tab === "reset-password" ? (
            <ResetForm />
          ) : (
            <AuthForm
              mode={tab === "register" ? "register" : "login"}
              providers={auth.providers}
              turnstileSiteKey={auth.turnstile_site_key}
            />
          )}
        </Suspense>
        {/* Ijtimoiy dalil + huquqiy havolalar (12-qaror).
            `Suspense` dan TASHQARIDA: u `api.stats()` ni kutadi va
            yiqilsa jim yo'qoladi — formani bloklamasligi kerak. */}
        <Suspense fallback={null}>
          <AuthProof />
        </Suspense>
      </Card>
    </AuthShell>
  );
}
