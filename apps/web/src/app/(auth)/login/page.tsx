import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { AuthForm } from "@/features/account";
import { AuthProof, AuthShell, AuthTabs } from "@/features/auth/server";
import { ResetForm } from "@/features/account";
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
  // Ilgari `null` edi: kirish bo'limida ko'rinadigan sarlavha yo'q edi va
  // sahifani faqat `document.title` nomlardi — ekran o'quvchi kartaning
  // nima ekanini aytolmasdi, ro'yxat bo'limida esa sarlavha bor edi.
  login: "auth.login",
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
    // Omit the key instead of setting it to `undefined`: Next merges metadata
    // with `for...in`, so `robots: undefined` wipes the root layout's noindex.
    ...(tab === "reset-password" ? { robots: { index: false, follow: false } } : {}),
  };
}

/** Uch bo'lim, bitta markazlashgan karta (1 va 18-qarorlar).
 *
 *  Ildiz manzil — `/login`. `?tab=` bo'lmasa kirish ochiladi, ya'ni
 *  `/login` ni yoddan yozgan odam ham to'g'ri joyga tushadi. */
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
        {/* Query (`next`, `link`, `social`, `token`) SERVERDA o'qiladi.
            Klient search-params hooki butun kartani Suspense fallback
            ga tiqib, avval «Yuklanmoqda», keyin formani chizardi —
            768 px register Lighthouse LCP 4.2 s / CLS 0.202
            edi (2026-09-21). */}
        <AuthTabs active={tab} next={nextOf(params)} />
        {tab === "reset-password" ? (
          <ResetForm token={one(params.token) ?? ""} />
        ) : (
          <AuthForm
            mode={tab === "register" ? "register" : "login"}
            providers={auth.providers}
            turnstileSiteKey={auth.turnstile_site_key}
            next={nextOf(params)}
            link={one(params.link)}
            social={one(params.social)}
          />
        )}
        {/* Ijtimoiy dalil (12-qaror). `api.stats()` formani
            bloklamasin — shu sabab `Suspense`. Karta `justify-center`
            da, shuning uchun joy OLDINDAN band: kelgan satr kartani
            pastdan ochib CLS yasamasin. */}
        <div className="min-h-[4.5rem]">
          <Suspense fallback={null}>
            <AuthProof />
          </Suspense>
        </div>
      </Card>
    </AuthShell>
  );
}
