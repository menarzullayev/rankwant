import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AuthForm } from "@/features/account";
import { AuthShell, AuthTabs } from "@/features/auth/server";
import { ResetForm } from "@/features/account";
import { fetchProviders } from "@/lib/api";
import { parseTab, DEFAULT_TAB, type TabId } from "@/lib/auth-tabs";
import { isSignedIn } from "@/lib/server-session";
import { safeNext } from "@/lib/site";
import { getLocale } from "@/i18n/server";
import { t, type MessageKey } from "@/i18n/messages";

/** Tab → page heading. Every tab has one: it is the page's `<h1>`, and it
 *  says what is being done ("Create account") while the button says the
 *  action. */
const TITLE: Record<TabId, MessageKey> = {
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
    title: t(locale, title),
    //: Tiklash bo'limida tokenli havola bo'lishi mumkin — qidiruvda
    //: kerak emas. Kirish va ro'yxat esa indekslanadi (SEO).
    // Omit the key instead of setting it to `undefined`: Next merges metadata
    // with `for...in`, so `robots: undefined` wipes the root layout's noindex.
    ...(tab === "reset-password" ? { robots: { index: false, follow: false } } : {}),
  };
}

/** Three tabs on one address, drawn in the two-column `AuthShell`.
 *
 *  `/login` is the root: without `?tab=` the sign-in form opens, so a
 *  typed-from-memory `/login` lands in the right place. */
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

  return (
    <AuthShell>
      <h1 className="mb-5 text-2xl font-bold rw-strong">
        {t(locale, TITLE[tab])}
      </h1>
      {/* The query (`next`, `link`, `social`, `token`) is read on the
          SERVER. A client search-params hook pushed the whole form into a
          Suspense fallback: "Loading" first, then the form — 768 px
          register measured LCP 4.2 s / CLS 0.202 (2026-09-21). */}
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
    </AuthShell>
  );
}
